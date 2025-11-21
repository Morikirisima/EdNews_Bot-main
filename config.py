import os
from dotenv import load_dotenv
import yaml

# Загружаем переменные окружения
load_dotenv()


# Создаем абсолютный путь к config.yaml
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Проверяем существует ли файл
if not os.path.exists(config_path):
    raise FileNotFoundError(f"❌ config.yaml не найден по пути: {config_path}")

# Читаем конфиг с правильным путем
with open(config_path, 'r', encoding='utf-8') as f:
    yaml_config = yaml.safe_load(f)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
GIGACHAT_ACCESS_TOKEN = os.getenv("GIGACHAT_ACCESS_TOKEN")

# Обработка ADMIN_IDS с проверкой на None
admin_ids_str = os.getenv("ADMIN_IDS")
ADMINS_IDS = []
if admin_ids_str:
    ADMINS_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]

# Настройки из YAML с значениями по умолчанию
TARGET_CHANNEL_ID = yaml_config.get('target_channel', '@ednews_ru')
PARSER_URL = yaml_config.get('parser_url', 'https://rg.ru/tema/obshestvo/obrazovanie')
PARSER_INTERVAL = yaml_config.get('parser_interval', 3600)
PUBLISH_DELAY = yaml_config.get('publish_delay', 5400)
DEBUG = yaml_config.get('debug', True)
MAX_POSTS_PER_RUN = yaml_config.get('max_posts_per_run', 1)
MAX_AUTO_POST_LENGTH = yaml_config.get('max_auto_post_length', 25000)

# Фильтры с вложенными значениями по умолчанию
filters_config = yaml_config.get('filters', {})
MANUAL_REVIEW_WORDS = filters_config.get('manual_review_words', [])
AD_FILTER_WORDS = filters_config.get('ad_filter_words', [])
MAX_AD_WORDS_COUNT = filters_config.get('max_ad_words_count', 3)
QUEUE_PAGE_SIZE = filters_config.get('queue_page_size', 10)
AD_FILTER_PATTERNS = filters_config.get('ad_patterns', [])

print("✅ Конфигурация загружена успешно")
print(f"📁 Config путь: {config_path}")
print(f"🔧 Режим отладки: {DEBUG}")
print(f"📰 URL парсера: {PARSER_URL}")