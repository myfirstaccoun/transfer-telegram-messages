from flask import Flask
import threading
import aiohttp
import asyncio
import random  # استيراد مكتبة العشوائية
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
SOURCE_CHANNEL = "@droos1111"
TARGET_CHANNEL = "@doros_dr_ahmed_rajab"
# SOURCE_CHANNEL = "@lllkkkkjjjpoi"
# TARGET_CHANNEL = "@polbhiogj"

client = TelegramClient(
    session="user_session",  # اسم ملف الجلسة
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
    
    # # تشغيل الفتش الدائم بفواصل عشوائية
    # asyncio.create_task(keep_alive())

    # التأكد من العضوية في القناة المصدر
    try:
        await client.get_entity(SOURCE_CHANNEL)
    except:
        await client.join_chat(SOURCE_CHANNEL)
        print("✅ تم الانضمام للقناة المصدر")

    # تعريف معالج الرسائل
    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def message_handler(event):
        try:
            await event.forward_to(TARGET_CHANNEL, drop_author=True)
            print(f"تم نقل الرسالة ({event.id}) بنجاح")
        except Exception as e:
            print(f"خطأ في النقل: {str(e)}")

    print("⚡ البوت يعمل الآن! استخدم Ctrl+C للإيقاف")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
