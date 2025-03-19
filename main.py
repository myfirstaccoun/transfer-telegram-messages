from flask import Flask
import threading
import aiohttp
import asyncio
import random
from telethon import TelegramClient, events
from telethon.events import NewMessage
from telethon.tl.custom.message import Message
import os
try: os.system("cls")
except: os.system("clear")

# تشغيل سيرفر Flask
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_server():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_server, daemon=True).start()

# ------------------- #

# ------------------- #
# الدوال المساعدة
# ------------------- #
def format_lesson(input_text: str):
    """تنسيق نص الدرس مع التاريخ الهجري"""
    from hijri_converter import Gregorian
    from datetime import datetime
    import re

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

# البيانات الأساسية
API_ID = 29224979
API_HASH = "c43959fea9767802e111a4c6cf3b16ec"

# قاموس القنوات (مصدر: هدف)
CHANNELS_MAP = {
    "@droos1111": "@doros_dr_ahmed_rajab",
    "@lllkkkkjjjpoi": "@polbhiogj"
}

client = TelegramClient(
    session="user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="TimeSync 1.0",
    device_model="Message Forwarder"
)

# دالة الـ keep_alive
async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://google.com") as response:
                    print(f"✅ Fetched Google, Status: {response.status}")
        except Exception as e:
            print(f"❌ Fetch error: {e}")
        
        wait_time = random.randint(300, 600)
        print(f"⏳ Waiting {wait_time} seconds before next fetch...")
        await asyncio.sleep(wait_time)

mess = []
check_audio = False

async def main():
    await client.start()

    # # تشغيل الفتش الدائم بفواصل عشوائية
    # asyncio.create_task(keep_alive())

    # الانضمام للقنوات المطلوبة
    for source_channel in CHANNELS_MAP.keys():
        try:
            await client.get_entity(source_channel)
        except:
            await client.join_chat(source_channel)
            print(f"✅ تم الانضمام للقناة: {source_channel}")

    # إنشاء معالج أحداث لكل قناة مصدر
    for source, target in CHANNELS_MAP.items():
        @client.on(events.NewMessage(chats=source))
        async def handler(event: NewMessage.Event, target=target):  # حل مشكلة الـ late binding
            try:
                if event.message.media:
                    global check_audio
                    check_audio = True
                
                mess.append({"event": event, "target": target})  # تخزين الحدث بشكل صحيح
                await send_filter(client)  # استدعاء الفلترة عند كل رسالة جديدة
                print(f"📤 تم استلام رسالة ({event.id}) من {source} إلى {target}")
            except Exception as e:
                print(f"❌ خطأ في النقل من {source}: {str(e)}")

    print("⚡ البوت يعمل الآن! استخدم Ctrl+C للإيقاف")
    await client.run_until_disconnected()

async def send_filter(client):
    global mess
    global check_audio
    text = []
    audio = []
    audio_description = []

    if len(mess) >= 3 or (len(mess) >= 2 and check_audio == False):
        for item in mess:
            event = item["event"]
            target = item["target"]

            if event.message.media:  # رسالة تحتوي على وسائط (مثل الصوت)
                audio.append({"event": event, "target": target})
            elif "#الدروس" in event.message.text:  # الرسائل التي تحتوي على وسم #الدروس
                audio_description.append({"event": event, "target": target})
            else:
                text.append({"event": event, "target": target})

        for item in text:
            await item["event"].forward_to(item["target"], drop_author=True)
        for item in audio:
            await item["event"].forward_to(item["target"], drop_author=True)
        for item in audio_description:
            await client.send_message(item["target"], format_lesson(item["event"].message.text))

        mess = []
        check_audio = False
        print("✅ الحمدلله تم إرسال الرسائل")

if __name__ == "__main__":
    asyncio.run(main())