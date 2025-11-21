import urllib3
import warnings



import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database.models.models import Post

from utils.filters import is_advertisement_content, needs_manual_review
import config
import re
import asyncio
import os

# ========== КОНФИГУРАЦИЯ GIGACHAT ==========

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
print("🔧 Инициализация конфигурации...")

GIGACHAT_ACCESS_TOKEN = getattr(config, 'GIGACHAT_ACCESS_TOKEN', None)

print(f"Токен из config: {GIGACHAT_ACCESS_TOKEN}")

if not GIGACHAT_ACCESS_TOKEN:
    GIGACHAT_ACCESS_TOKEN = os.getenv("GIGACHAT_ACCESS_TOKEN")
    print(f"Токен из окружения: {GIGACHAT_ACCESS_TOKEN}")
    if not GIGACHAT_ACCESS_TOKEN:
        print("❌ GIGACHAT_ACCESS_TOKEN не найден!")
        GIGACHAT_ACCESS_TOKEN = "test_token"
    else:
        print("✅ Токен найден в переменных окружения")
else:
    print("✅ Токен найден в config")

print(f"Итоговый токен: {GIGACHAT_ACCESS_TOKEN[:20]}..." if GIGACHAT_ACCESS_TOKEN and len(GIGACHAT_ACCESS_TOKEN) > 20 else f"Итоговый токен: {GIGACHAT_ACCESS_TOKEN}")
GIGACHAT_MODEL = "GigaChat"
GIGACHAT_MAX_TOKENS = 500
GIGACHAT_TEMPERATURE = 0.3

SYSTEM_PROMPT = """Ты - помощник, который структурирует тексты статей, делая их более читаемыми без значительного сокращения."""

USER_PROMPT_TEMPLATE = """Обработай следующий текст по правилам:

{text}"""

ADVERTISING_KEYWORD = "[ADVERTISING]"
PROHIBITED_KEYWORD = "[PROHIBITED]"


class EnhancedParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def parse_new_posts(self) -> list:
        """Основной метод парсинга с улучшенным извлечением контента"""
        try:
            print(f"🔍 Парсим {config.PARSER_URL}")
            response = self.session.get(config.PARSER_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html5lib')

            posts_data = self._extract_posts(soup)
            print(f"✅ Найдено {len(posts_data)} постов")

            # Обрабатываем тексты через GigaChat
            processed_posts = await self._process_with_gigachat(posts_data)

            return processed_posts

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return []

    def _extract_posts(self, soup) -> list:
        """Извлекает посты - упрощенная версия"""
        posts = []

        print("🔍 Поиск статей на странице...")

        # Простой способ: ищем все ссылки которые выглядят как статьи
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']
            text = link.get_text(strip=True)

            # Фильтруем ссылки на статьи
            if (href and
                    ('/20' in href or '/news' in href or '/article' in href) and
                    len(text) > 10 and
                    not href.startswith(('javascript:', 'mailto:', '#'))):

                # Создаем абсолютный URL
                if href.startswith('/'):
                    url = 'https://rg.ru' + href
                else:
                    url = href

                # Создаем пост
                post_data = {
                    'title': text,
                    'preview_content': "",
                    'original_content': "",
                    'processed_content': "",
                    'source_url': url,
                    'published_at': datetime.now(),
                    'image_url': "",
                    'is_valid': True
                }

                # Получаем полный текст
                if url:
                    post_data['original_content'] = self._get_full_content(url)

                posts.append(post_data)
                print(f"✅ Добавлен пост: {text[:60]}...")

        return posts

    def _parse_article(self, article) -> dict:
        """Парсит отдельную статью с улучшенным извлечением контента"""
        try:
            title_elem = (article.find('h3') or
                          article.find('h2') or
                          article.find('span', class_='ItemOfListStandard_title__Ajjlf') or
                          article.find('a').find('span') if article.find('a') else None)

            title = title_elem.get_text().strip() if title_elem else "Без заголовка"

            if not title or title == "Без заголовка":
                return self._create_invalid_post("Без заголовка")

            link_elem = article.find('a')
            url = link_elem.get('href') if link_elem else ""
            if url and url.startswith('/'):
                url = 'https://rg.ru' + url

            content_elem = (article.find('p') or
                            article.find('div', class_='preview') or
                            article.find('div', class_='ItemOfListStandard_announce__cOc_i'))
            preview_content = content_elem.get_text().strip() if content_elem else ""

            full_content = ""
            if url:
                full_content = self._get_full_content(url)

            return {
                'title': title,
                'preview_content': preview_content,
                'original_content': full_content,
                'processed_content': "",
                'source_url': url,
                'published_at': datetime.now(),
                'image_url': self._extract_image(article),
                'is_valid': True
            }

        except Exception as e:
            print(f"Ошибка парсинга статьи: {e}")
            return self._create_invalid_post(f"Ошибка: {str(e)}")

    @staticmethod
    def _create_invalid_post(title: str) -> dict:
        """Создает невалидный пост (статический метод)"""
        return {
            'title': title,
            'preview_content': "",
            'original_content': "",
            'processed_content': "",
            'source_url': "",
            'published_at': datetime.now(),
            'image_url': "",
            'is_valid': False
        }
    @staticmethod
    def _extract_image(article) -> str:
        """Извлекает URL изображения (статический метод)"""
        try:
            image_element = article.find('div', class_='ImageIcon_root__XuGMY')
            if not image_element:
                image_element = article.find('img')

            if image_element:
                img_tag = image_element.find('img') if image_element.name == 'div' else image_element
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://rg.ru' + img_url
                    return img_url
        except Exception as e:
            print(f"Ошибка извлечения изображения: {e}")

        return ""

    def _get_full_content(self, url: str) -> str:
        """Получает полный текст статьи"""
        try:
            if not url:
                return ""

            print(f"    📖 Получаем полный текст: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            content_blocks = [
                soup.find('div',
                          class_='PageContentCommonStyling_text__CKOzO commonArticle_text__ul5uZ commonArticle_zoom__SDMjc'),
                soup.find('div', class_='PageArticleContent_lead__l9TkG commonArticle_zoom__SDMjc'),
                soup.find('div', class_='PageContentCommonStyling_text__CKOzO'),
                soup.find('div', class_='article-content'),
                soup.find('div', class_='article-body'),
                soup.find('article')
            ]

            article_text = ""
            for block in content_blocks:
                if block:
                    paragraphs = block.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 10:
                            article_text += text + "\n\n"

                    if article_text:
                        print(f"    ✅ Найден текст: {len(article_text)} символов")
                        article_text = re.sub(r'\n\s*\n', '\n\n', article_text.strip())
                        return article_text

            if not article_text:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 50:
                        article_text += text + "\n\n"

                if article_text:
                    print(f"    ⚠️ Текст найден через fallback: {len(article_text)} символов")
                    return article_text

            print("    ❌ Текст не найден")
            return ""

        except Exception as e:
            print(f"    ❌ Ошибка получения полного текста: {e}")
            return f"Ошибка получения контента: {str(e)}"

    async def _process_with_gigachat(self, posts_data: list) -> list:
        """Обрабатывает тексты через GigaChat API"""
        processed_posts = []

        for post_data in posts_data:
            if not post_data or not post_data.get('is_valid', True):
                print(f"    ⏭️ Пропускаем невалидный пост: {post_data.get('title', 'No title')}")
                continue

            original_text = post_data.get('original_content', '')

            if not original_text or len(original_text) < 300:
                post_data['processed_content'] = original_text
                post_data['processing_status'] = 'too_short'
                processed_posts.append(post_data)
                continue

            try:
                print(f"    🤖 Обрабатываем через GigaChat: {post_data['title'][:50]}...")
                # Убираем await для синхронного вызова
                processed_text = self._call_gigachat_api(original_text)

                if processed_text == ADVERTISING_KEYWORD:
                    post_data['processed_content'] = original_text
                    post_data['processing_status'] = 'advertising'
                    post_data['is_valid'] = False
                    print(f"    ⚠️ Обнаружена реклама: {post_data['title'][:50]}...")

                elif processed_text == PROHIBITED_KEYWORD:
                    post_data['processed_content'] = original_text
                    post_data['processing_status'] = 'prohibited'
                    post_data['is_valid'] = False
                    print(f"    ⚠️ Запрещенный контент: {post_data['title'][:50]}...")

                else:
                    original_len = len(original_text)
                    processed_len = len(processed_text)

                    if processed_len < 50:
                        post_data['processed_content'] = original_text
                        post_data['processing_status'] = 'api_error'
                        print(f"    ⚠️ Ошибка API (короткий ответ): {post_data['title'][:50]}...")
                    else:
                        post_data['processed_content'] = processed_text
                        post_data['processing_status'] = 'processed'
                        reduction = ((original_len - processed_len) / original_len) * 100
                        print(
                            f"    ✅ Обработан: {post_data['title'][:50]}... ({processed_len}/{original_len} chars, -{reduction:.1f}%)")

                processed_posts.append(post_data)
                await asyncio.sleep(1)  # Оставляем задержку между запросами

            except Exception as e:
                print(f"❌ Ошибка обработки GigaChat: {e}")
                post_data['processed_content'] = original_text
                post_data['processing_status'] = 'api_error'
                processed_posts.append(post_data)

        return processed_posts

    @staticmethod
    def _call_gigachat_api(text: str) -> str:
        """Вызывает GigaChat API для обработки текста"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GIGACHAT_ACCESS_TOKEN}',
                'Accept': 'application/json'
            }

            payload = {
                "model": GIGACHAT_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": USER_PROMPT_TEMPLATE.format(text=text)
                    }
                ],
                "max_tokens": GIGACHAT_MAX_TOKENS,
                "temperature": GIGACHAT_TEMPERATURE
            }

            response = requests.post(
                GIGACHAT_API_URL,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # ← ДОБАВЬ ЭТУ СТРОКУ ДЛЯ ОТКЛЮЧЕНИЯ SSL ПРОВЕРКИ
            )

            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"    ❌ Ошибка вызова GigaChat API: {e}")
            raise

async def process_parsed_posts(posts_data: list) -> list:
    """Обрабатывает спарсенные посты: фильтрует и определяет статусы"""
    processed_posts = []

    for post_data in posts_data:
        if not post_data or not post_data.get('is_valid', True):
            continue

        content_for_filtering = post_data.get('processed_content') or post_data.get('original_content', '')
        full_text = f"{post_data['title']} {content_for_filtering}"

        processing_status = post_data.get('processing_status', '')

        if (processing_status in ['advertising', 'prohibited'] or
                is_advertisement_content(full_text)):
            status = "rejected"
            print(f"🚫 Отклонен: {post_data['title'][:50]}...")

        elif (processing_status == 'api_error' or
              needs_manual_review(full_text) or
              not post_data.get('source_url')):
            status = "draft"
            print(f"📝 На модерацию: {post_data['title'][:50]}...")

        else:
            status = "parsed"
            print(f"✅ В очередь: {post_data['title'][:50]}...")

        processed_posts.append({
            **post_data,
            'status': status,
            'needs_review': status == "draft"
        })

    return processed_posts


async def save_posts_to_db(posts: list, db_session):
    """Сохраняет посты в базу данных с обработанным контентом"""
    from sqlalchemy import select

    saved_count = 0
    skipped_count = 0

    for post_data in posts:
        if not post_data or not post_data.get('is_valid', True):
            skipped_count += 1
            continue

        try:
            # ФИКС: правильное использование SQLAlchemy в условии WHERE
            if post_data.get('source_url'):
                existing_post = await db_session.execute(
                    select(Post).where(Post.source_url == post_data['source_url'])
                )
                if existing_post.scalar():
                    print(f"⏭️ Пропускаем дубликат: {post_data['title'][:50]}...")
                    skipped_count += 1
                    continue

            # Создаем новый пост
            new_post = Post(
                title=post_data['title'],
                content=post_data.get('processed_content') or post_data.get('original_content', ''),
                source_url=post_data.get('source_url', ''),
                status=post_data['status'],
                preview_content=post_data.get('preview_content', ''),
                original_content=post_data.get('original_content', ''),
                image_url=post_data.get('image_url', ''),
                processing_status=post_data.get('processing_status', 'not_processed'),
                published_at=post_data.get('published_at', datetime.now())
            )

            db_session.add(new_post)
            saved_count += 1
            print(f"💾 Сохранен: {post_data['title'][:50]}... (статус: {post_data['status']})")

        except Exception as e:
            print(f"❌ Ошибка сохранения поста {post_data.get('title', 'Unknown')}: {e}")
            skipped_count += 1
            continue

    try:
        await db_session.commit()
        print(f"💾 Всего: {len(posts)} постов, сохранено: {saved_count}, пропущено: {skipped_count}")
        return saved_count
    except Exception as e:
        print(f"❌ Ошибка коммита в БД: {e}")
        await db_session.rollback()
        return 0

