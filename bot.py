from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)

TOKEN = "8270497543:AAFzOmpgkYveC9toVl3bVXiMYV6KtzV9snc"
MANAGERS = [358564, 183592069]  # ID

# Хранение соответствия: message_id 358564 → client_id
reply_map = {}  


async def handle_client_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client_id = update.message.chat_id
    text = update.message.text

    # Пересылаем менеджерам
    for manager_id in MANAGERS:
        sent = await context.bot.send_message(
            manager_id,
            f"💬 Клиент #{client_id}:\n{text}"
        )
        # Запоминаем, что на это сообщение менеджер может ответить
        reply_map[sent.message_id] = client_id


async def handle_manager_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager_id = update.message.chat_id
    text = update.message.text

    # Проверяем, является ли сообщение ответом на сообщение бота (reply)
    if update.message.reply_to_message is None:
        await context.bot.send_message(
            chat_id=manager_id,
            text="Ответьте на сообщение клиента через 'Ответить'."
        )
        return

    reply_msg = update.message.reply_to_message

    # Проверяем, есть ли это сообщение в карте диалогов
    if reply_msg.message_id not in reply_map:
        await update.message.reply_text("Не найден клиент. Ответьте через 'Ответить' на сообщение клиента.")
        return

    client_id = reply_map[reply_msg.message_id]

    # Отправляем клиенту
    await context.bot.send_message(
        chat_id=client_id,
        text=text
    )

    # Дублируем второму менеджеру
    for mgr in MANAGERS:
        if mgr != manager_id:
            await context.bot.send_message(
                chat_id=mgr,
                text=f"✉️ Ответ от менеджера #{manager_id} клиенту #{client_id}:\n{text}"
            )


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Клиенты — все, кто НЕ менеджеры
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.Chat(chat_id=MANAGERS), handle_client_message)
    )

    # Менеджеры
    app.add_handler(
        MessageHandler(filters.Chat(chat_id=MANAGERS) & filters.TEXT, handle_manager_message)
    )

    print("Бот запущен и работает...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())