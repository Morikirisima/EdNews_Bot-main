import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def find_and_test_bot():
    """Находит и тестирует бота"""
    print("🔍 ПОИСК И ТЕСТ БОТА")

    # Возможные имена файлов бота
    bot_files = [
        'bot.py', 'telegram_bot.py', 'main.py',
        'bot/bot.py', 'bot/__init__.py', 'src/bot.py'
    ]

    # Проверяем какие файлы существуют
    existing_bots = []
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            existing_bots.append(bot_file)
            print(f"✅ Найден: {bot_file}")

    if not existing_bots:
        print("❌ Файлы бота не найдены!")
        # Покажем что есть в проекте
        files = [f for f in os.listdir('.') if f.endswith('.py')]
        print(f"📁 Python файлы в проекте: {files}")
        return

    # Пробуем импортировать из первого найденного файла
    bot_file = existing_bots[0]
    print(f"🔄 Пробуем импортировать из: {bot_file}")

    try:
        # Убираем расширение .py для импорта
        module_name = bot_file.replace('.py', '').replace('/', '.')
        if module_name.startswith('.'):
            module_name = module_name[1:]

        print(f"📦 Импортируем модуль: {module_name}")

        # Динамический импорт
        bot_module = __import__(module_name, fromlist=[''])
        print(f"✅ Модуль загружен: {bot_module}")

        # Проверяем есть ли необходимые атрибуты
        if hasattr(bot_module, 'bot'):
            print("✅ Бот найден в модуле")
        else:
            print("❌ Бот не найден в модуле")

        if hasattr(bot_module, 'dp'):
            print("✅ Диспетчер найден")
        else:
            print("❌ Диспетчер не найден")

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()


async def test_channel_access():
    """Тестирует доступ к каналу"""
    print("\n📢 ТЕСТ ДОСТУПА К КАНАЛУ")

    try:
        import config
        print(f"🎯 Канал: {config.TARGET_CHANNEL_ID}")
        print(f"🔑 Токен бота: {'✅' if config.BOT_TOKEN else '❌'}")

        # Простой тест с requests
        import requests
        bot_token = config.BOT_TOKEN
        if bot_token:
            # Проверяем что бот жив
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print("✅ Бот активен и токен валиден")
                bot_info = response.json()
                print(f"   Имя бота: {bot_info['result']['first_name']}")
                print(f"   Username: @{bot_info['result']['username']}")
            else:
                print(f"❌ Ошибка API Telegram: {response.status_code}")
        else:
            print("❌ Токен бота не найден")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(find_and_test_bot())
    asyncio.run(test_channel_access())