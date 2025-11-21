import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database.models.models import Post  # ← правильный импорт
from utils.filters import is_advertisement_content, needs_manual_review
import config


class SimpleParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def parse_new_posts(self) -> list:
        """Основной метод парсинга"""
        try:
            print(f"🔍 Парсим {config.PARSER_URL}")
            response = self.session.get(config.PARSER_URL)
            soup = BeautifulSoup(response.content, 'html.parser')

            posts_data = self._extract_posts(soup)
            print(f"✅ Найдено {len(posts_data)} постов")
            return posts_data

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return []

    def _extract_posts(self, soup) -> list:
        """Извлекает посты из HTML"""
        posts = []

        articles = soup.find_all('article', limit=10)
        if not articles:
            articles = soup.find_all('div', class_='ItemOfListStandard_item__eAfc4', limit=10)

        for article in articles:
            post_data = self._parse_article(article)
            if post_data and post_data.get('title') and post_data['title'] != "Без заголовка":
                posts.append(post_data)

        return posts

    def _parse_article(self, article) -> dict:
        """Парсит отдельную статью"""
        try:
            title_elem = (article.find('h3') or
                          article.find('h2') or
                          article.find('span', class_='ItemOfListStandard_title__Ajjlf') or
                          article.find('a').find('span') if article.find('a') else None)

            title = title_elem.get_text().strip() if title_elem else "Без заголовка"

            link_elem = article.find('a')
            url = link_elem.get('href') if link_elem else ""
            if url and url.startswith('/'):
                url = 'https://rg.ru' + url

            content_elem = (article.find('p') or
                            article.find('div', class_='preview') or
                            article.find('div', class_='ItemOfListStandard_announce__cOc_i'))
            content = content_elem.get_text().strip() if content_elem else ""

            if not content and url:
                content = self._get_full_content(url)

            return {
                'title': title,
                'content': content,
                'source_url': url,
                'published_at': datetime.now()
            }

        except Exception as e:
            print(f"Ошибка парсинга статьи: {e}")
            return {
                'title': "Ошибка парсинга",
                'content': "",
                'source_url': "",
                'published_at': datetime.now()
            }

    def _get_full_content(self, url: str) -> str:
        """Получает полный текст статьи"""
        try:
            if not url:
                return ""

            print(f"    📖 Получаем полный текст: {url}")
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            content_blocks = [
                soup.find('div', class_='PageArticleContent_lead__l9TkG'),
                soup.find('div', class_='PageContentCommonStyling_text__CKOzO'),
                soup.find('div', class_='article-content'),
                soup.find('div', class_='article-body'),
                soup.find('article')
            ]

            for block in content_blocks:
                if block:
                    paragraphs = block.find_all('p')
                    text = '\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                    if text:
                        print(f"    ✅ Найден текст: {len(text)} символов")
                        return text

            print("    ❌ Текст не найден")
            return ""

        except Exception as e:
            print(f"    ❌ Ошибка получения полного текста: {e}")
            return ""


async def process_parsed_posts(posts_data: list) -> list:
    """Обрабатывает спарсенные посты: фильтрует и определяет статусы"""
    processed_posts = []

    for post_data in posts_data:
        if not post_data:
            continue

        full_text = f"{post_data['title']} {post_data['content']}"

        if is_advertisement_content(full_text):
            status = "rejected"
            print(f"🚫 Отклонен (реклама): {post_data['title']}")

        elif needs_manual_review(full_text):
            status = "draft"
            print(f"📝 На модерацию: {post_data['title']}")

        else:
            status = "parsed"
            print(f"✅ В очередь: {post_data['title']}")

        processed_posts.append({
            **post_data,
            'status': status,
            'needs_review': status == "draft"
        })

    return processed_posts


async def save_posts_to_db(posts: list, db_session):
    """Сохраняет посты в базу данных"""
    from sqlalchemy import select

    saved_count = 0

    for post_data in posts:
        if not post_data:
            continue

        try:
            # Проверяем дубликат - используем Post (с большой буквы)
            existing_post = await db_session.execute(
                select(Post).where(Post.source_url == post_data['source_url'])  # ← Post
            )
            if existing_post.scalar():
                print(f"⏭️ Пропускаем дубликат: {post_data['title']}")
                continue

            # Создаем новый пост - используем Post (с большой буквы)
            new_post = Post(  # ← Post
                title=post_data['title'],
                content=post_data['content'],
                source_url=post_data['source_url'],
                status=post_data['status']
            )

            db_session.add(new_post)
            saved_count += 1
            print(f"💾 Сохранен: {post_data['title']}")

        except Exception as e:
            print(f"❌ Ошибка сохранения поста: {e}")
            continue

    await db_session.commit()
    print(f"💾 Всего сохранено {saved_count} постов в БД")
    return saved_count