from telethon import TelegramClient, events
import asyncio

# البيانات الأساسية
API_ID = 29224979
API_HASH = "c43959fea9767802e111a4c6cf3b16ec"
SOURCE_CHANNEL = "@lllkkkkjjjpoi"
TARGET_CHANNEL = "@polbhiogj"

client = TelegramClient(
    session="user_session",  # اسم ملف الجلسة
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="TimeSync 1.0",
    device_model="Message Forwarder"
)

async def main():
    # بدء تسجيل الدخول
    await client.start()
    
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
