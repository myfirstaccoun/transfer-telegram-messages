from flask import Flask
import threading
import aiohttp
import asyncio
import random
from telethon import TelegramClient, events

# تشغيل سيرفر Flask للحفاظ على تشغيل التطبيق في Koyeb
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200  # Koyeb هيشوف إن التطبيق شغال

def run_server():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_server, daemon=True).start()

# ------------------- #

# البيانات الأساسية
API_ID = 29224979
API_HASH = "c43959fea9767802e111a4c6cf3b16ec"

# ✅ تعريف القنوات المصدر والمستهدفة كـ "قاموس" (dictionary)
CHANNELS_MAP = {
    "@droos1111": "@doros_dr_ahmed_rajab",  # القناة 1
    "@lllkkkkjjjpoi": "@polbhiogj"  # القناة 2
}

# تشغيل الجلسة
client = TelegramClient(
    session="user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="TimeSync 1.0",
    device_model="Message Forwarder"
)

# دالة لعمل fetch بفواصل عشوائية بين 5 و 10 دقائق
async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://google.com") as response:
                    print(f"✅ Fetched Google, Status: {response.status}")
        except Exception as e:
            print(f"❌ Fetch error: {e}")
        
        wait_time = random.randint(300, 600)  # وقت عشوائي بين 5 و 10 دقائق
        print(f"⏳ Waiting {wait_time} seconds before next fetch...")
        await asyncio.sleep(wait_time)

async def main():
    await client.start()

    # # تشغيل keep_alive بفواصل عشوائية
    # asyncio.create_task(keep_alive())  # ✅ تشغيل الفانكشن بدون تعطيل الكود الأساسي
    
    # التأكد من العضوية في كل القنوات المصدر
    for source_channel in CHANNELS_MAP.keys():
        try:
            await client.get_entity(source_channel)
        except:
            await client.join_chat(source_channel)
            print(f"✅ تم الانضمام للقناة: {source_channel}")

    # تعريف معالج الرسائل لعدة قنوات
    @client.on(events.NewMessage(chats=list(CHANNELS_MAP.keys())))  
    async def message_handler(event):
        source = event.chat.username  # القناة المصدر
        if source in CHANNELS_MAP:
            target_channel = CHANNELS_MAP[source]  # القناة المستهدفة
            try:
                await event.forward_to(target_channel, drop_author=True)
                print(f"📤 تم نقل رسالة ({event.id}) من {source} إلى {target_channel}")
            except Exception as e:
                print(f"❌ خطأ في النقل من {source}: {str(e)}")

    print("⚡ البوت يعمل الآن! استخدم Ctrl+C للإيقاف")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
