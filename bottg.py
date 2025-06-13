import os
import requests
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка токена и базового URL
TOKEN = '7671395940:AAHwqDqy-PD8OfhFdjvCIjTE2u2yQ2yZ7wo'
BASE_URL = 'https://newvaybcodingtrue.onrender.com/'
session_token = None

# Команда /login - вход в систему
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global session_token
    if len(context.args) != 2:
        await update.message.reply_text('Использование: /login <login> <password>')
        return
    login, password = context.args
    try:
        response = requests.post(f'{BASE_URL}/login', json={'login': login, 'password': password})
        response.raise_for_status()
        session_token = response.json()['token']
        await update.message.reply_text('Авторизация успешна.')
    except requests.exceptions.RequestException:
        await update.message.reply_text('Ошибка авторизации. Неверный логин или пароль.')

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
        headers = {'Authorization': f'Bearer {session_token}'}
        response = requests.get(f'{BASE_URL}/api/items', headers=headers)
        response.raise_for_status()
        items = response.json()
        if items:
            message = '\n'.join([f"{index + 1} / {item['text']} / [{item['id']}]" for index, item in enumerate(items)])
        else:
            message = 'Список пуст.'
        await update.message.reply_text(message)
    except requests.exceptions.RequestException:
        await update.message.reply_text('Ошибка получения списка.')

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
        headers = {'Authorization': f'Bearer {session_token}'}
        response = requests.post(f'{BASE_URL}/add', json={'text': text}, headers=headers)
        response.raise_for_status()
        await update.message.reply_text('Задача добавлена.')
    except requests.exceptions.RequestException:
        await update.message.reply_text('Ошибка добавления задачи.')

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
        headers = {'Authorization': f'Bearer {session_token}'}
        response = requests.post(f'{BASE_URL}/delete', json={'id': task_id}, headers=headers)
        response.raise_for_status()
        await update.message.reply_text('Задача удалена.')
    except requests.exceptions.RequestException:
        await update.message.reply_text('Ошибка удаления задачи.')

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