from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # ← убрал func
from database.models.models import Post
from datetime import datetime  # ← добавил datetime


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_by_url(self, source_url: str) -> Post | None:
        """Проверяет есть ли пост с таким URL (антидубликация)"""
        result = await self.session.execute(
            select(Post).where(Post.source_url == source_url)
        )
        return result.scalar_one_or_none()

    async def create_post(self, post_data: dict) -> Post:
        """Создает новый пост с проверкой на дубликаты"""
        # Проверяем нет ли уже поста с таким URL
        existing_post = await self.get_post_by_url(post_data["source_url"])
        if existing_post:
            return existing_post

        post = Post(**post_data)
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_unpublished_posts(self, limit: int = 10) -> list[Post]:
        """Получает неопубликованные посты"""
        result = await self.session.execute(
            select(Post)
            .where(Post.status == "parsed")  # ← строка "parsed" это нормально
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_published(self, post_id: int, telegram_message_id: int):
        """Отмечает пост как опубликованный"""
        post = await self.session.get(Post, post_id)
        if post:
            post.status = "published"
            post.published_at = datetime.now()  # ← используем datetime
            post.telegram_message_id = telegram_message_id
            await self.session.commit()