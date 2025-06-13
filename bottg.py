import os
import mysql.connector
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка токена и конфигурации базы данных
TOKEN = '7671395940:AAHwqDqy-PD8OfhFdjvCIjTE2u2yQ2yZ7wo'
db_config = {
    'host': 'sql7.freesqldatabase.com',
    'user': 'sql7784455',
    'password': 'xxB1ERVxEi',
    'database': 'sql7784455',
    'port': 3306
}
session_token = None  # Хранит ID пользователя после авторизации

# Функция для подключения к БД
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Команда /login - вход в систему
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    if len(context.args) != 2:
        await update.message.reply_text('Использование: /login <login> <password>')
        return
    login, password = context.args
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s", (login, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session_token = user['id']  # Используем ID пользователя как токен
            await update.message.reply_text('Авторизация успешна.')
        else:
            await update.message.reply_text('Ошибка авторизации. Неверный логин или пароль.')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)}')

# Команда /logout - выход из учетной записи
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    session_token = None
    await update.message.reply_text('Вы успешно вышли из учетной записи.')

# Команда /showcom - показать доступные команды
async def showcom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = """
Доступные команды:
- /login <login> <password> - Войти в систему
- /logout - Выйти из учетной записи
- /list - Показать список задач
- /add <текст> - Добавить задачу
- /delete <id> - Удалить задачу по ID
- /showcom - Показать доступные команды
    """
    await update.message.reply_text(commands)

# Команда /list - показать список задач
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    if not session_token:
        await update.message.reply_text('Ошибка: вы не авторизованы. Используйте /login <login> <password>.')
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, text FROM items WHERE user_id = %s", (session_token,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        if items:
            message = '\n'.join([f"{index + 1} / {item['text']} / [{item['id']}]" for index, item in enumerate(items)])
        else:
            message = 'Список пуст.'
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)}')

# Команда /add - добавить задачу
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    if not session_token:
        await update.message.reply_text('Ошибка: вы не авторизованы. Используйте /login <login> <password>.')
        return
    if len(context.args) < 1:
        await update.message.reply_text('Использование: /add <текст>')
        return
    text = ' '.join(context.args)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (text, user_id) VALUES (%s, %s)", (text, session_token))
        conn.commit()
        cursor.close()
        conn.close()
        await update.message.reply_text('Задача добавлена.')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)}')

# Команда /delete - удалить задачу по ID
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    if not session_token:
        await update.message.reply_text('Ошибка: вы не авторизованы. Используйте /login <login> <password>.')
        return
    if len(context.args) != 1:
        await update.message.reply_text('Использование: /delete <id>')
        return
    task_id = context.args[0]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = %s AND user_id = %s", (task_id, session_token))
        conn.commit()
        cursor.close()
        conn.close()
        await update.message.reply_text('Задача удалена.')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)}')

# Установка команд в меню Telegram
async def set_commands(application):
    commands = [
        BotCommand("login", "Войти в систему: /login <login> <password>"),
        BotCommand("logout", "Выйти из учетной записи"),
        BotCommand("list", "Показать список задач"),
        BotCommand("add", "Добавить задачу: /add <текст>"),
        BotCommand("delete", "Удалить задачу: /delete <id>"),
        BotCommand("showcom", "Показать доступные команды")
    ]
    await application.bot.set_my_commands(commands)

# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(CommandHandler("showcom", showcom))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("delete", delete_task))

    # Установка команд в меню
    application.post_init = set_commands

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
