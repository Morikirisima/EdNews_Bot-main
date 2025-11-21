import os
from dotenv import  load_dotenv
import yaml

load_dotenv()

with open('config.yaml', 'r', encoding='utf-8') as f:
    yaml_config = yaml.safe_load(f)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMINS_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS").split(",") if x.strip()]


TARGET_CHANNEL_ID = yaml_config['target_channel']
PARSER_URL = yaml_config['parser_url']
PARSER_INTERVAL = yaml_config['parser_interval']
PUBLISH_DELAY = yaml_config['publish_delay']
DEBUG = yaml_config['debug']
MAX_POSTS_PER_RUN = yaml_config['max_posts_per_run']
MAX_AUTO_POST_LENGTH = yaml_config['max_auto_post_length']


MANUAL_REVIEW_WORDS = yaml_config['filters']['manual_review_words']
AD_FILTER_WORDS = yaml_config['filters']['ad_filter_words']
MAX_AD_WORDS_COUNT = yaml_config['filters']['max_ad_words_count']
QUEUE_PAGE_SIZE = yaml_config['filters']['queue_page_size']
AD_FILTER_PATTERNS = yaml_config['filters']['ad_patterns']


