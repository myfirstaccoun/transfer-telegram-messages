from flask import Flask
import threading
import asyncio
from telethon import TelegramClient, events
from hijri_converter import Gregorian
from datetime import datetime
import re

# ------------------- #
# إعداد سيرفر Flask للحفاظ على التشغيل
# ------------------- #
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_server():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_server, daemon=True).start()

# ------------------- #
# الدوال المساعدة
# ------------------- #
def format_lesson(input_text: str):
    """تنسيق نص الدرس مع التاريخ الهجري"""
    arabic_weekdays = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    lines = input_text.strip().split('\n')
    processed = []
    whatsapp_tag = '#الدروس_العلمية_اليومية_واتساب'
    
    for line in lines:
        stripped = line.strip()
        if stripped == whatsapp_tag:
            continue
        stripped = re.sub(r'^([🌹🎙])\uFE0F? *', r'\1 ', stripped)
        processed.append(stripped)
    
    # استخراج الأجزاء المهمة
    emoji_lines = [line for line in processed if line.startswith(('🌹', '🎙'))]
    hashtags = [line for line in processed if line.startswith('#') and line != whatsapp_tag]
    hashtags.append('#درس_صوت')
    
    # توليد التاريخ الهجري
    today = datetime.today()
    g = Gregorian(today.year, today.month, today.day)
    h = g.to_hijri()
    hijri_date = f"{arabic_weekdays[today.weekday()]} {h.day} {h.month_name('ar')} {h.year}هـ"
    
    # تجميع الأجزاء
    sections = []
    if emoji_lines:
        sections.extend(emoji_lines[:2])
    if hashtags:
        sections.append('\n'.join(hashtags))
    sections.append(hijri_date)
    
    return '\n\n'.join(sections)

# ------------------- #
# إعدادات التليجرام
# ------------------- #
API_ID = 29224979
API_HASH = "c43959fea9767802e111a4c6cf3b16ec"
CHANNELS_MAP = {
    "@droos1111": "@doros_dr_ahmed_rajab",
    "@lllkkkkjjjpoi": "@polbhiogj"
}

client = TelegramClient(
    session="user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="1.0",
    device_model="Message Forwarder"
)

# ------------------- #
# إدارة طوابير الرسائل
# ------------------- #
message_queues = {}

async def process_and_send(source: str, target: str):
    """معالجة وإرسال الرسائل المجمعة"""
    queue = message_queues.get(source, [])
    
    # تصنيف الرسائل
    text_msg = next((m for m in queue if not m.audio and "#الدروس" not in m.text), None)
    audio_msg = next((m for m in queue if m.audio), None)
    tag_msg = next((m for m in queue if "#الدروس" in m.text), None)
    
    try:
        # إرسال بالترتيب المطلوب
        if text_msg:
            await text_msg.forward_to(target)
            print(f"✅ تم إرسال النص: {text_msg.id}")
        
        if audio_msg:
            await audio_msg.forward_to(target)
            print(f"✅ تم إرسال الصوت: {audio_msg.id}")
        
        if tag_msg:
            formatted = format_lesson(tag_msg.text)
            await client.send_message(target, formatted)
            print(f"✅ تم إرسال الوسم المنسق: {tag_msg.id}")
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {str(e)}")
    finally:
        # تفريغ الطابور بعد الإرسال
        message_queues[source] = []

# ------------------- #
# معالج الأحداث الرئيسي
# ------------------- #
@client.on(events.NewMessage)
async def message_handler(event):
    source = event.chat.username
    target = CHANNELS_MAP.get(source)
    
    if not source or not target:
        return
    
    # إضافة الرسالة للطابور
    if source not in message_queues:
        message_queues[source] = []
    message_queues[source].append(event.message)
    
    # التحقق من شروط الإرسال
    queue = message_queues[source]
    has_text = any(not m.audio and "#الدروس" not in m.text for m in queue)
    has_tag = any("#الدروس" in m.text for m in queue)
    has_audio = any(m.audio for m in queue)
    
    send_condition = (
        len(queue) >= 3 or  # 3 رسائل (نص، صوت، وسم)
        (len(queue) >= 2 and has_text and has_tag and not has_audio)  # حالتين بدون صوت
    )
    
    if send_condition:
        await process_and_send(source, target)

# ------------------- #
# تشغيل البوت
# ------------------- #
async def main():
    await client.start()
    
    # الانضمام للقنوات المطلوبة
    for source in CHANNELS_MAP:
        try:
            await client.get_entity(source)
        except:
            await client.join_chat(source)
            print(f"✅ انضممت للقناة: {source}")
    
    print("⚡ البوت يعمل بنجاح!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
