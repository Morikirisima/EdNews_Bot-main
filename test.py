import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_parser():
    print("🚀 ТЕСТ ИСПРАВЛЕННОГО ПАРСЕРА")
    print("=" * 50)

    try:
        from parsers.parser import EnhancedParser

        parser = EnhancedParser()
        posts = await parser.parse_new_posts()

        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"Всего постов: {len(posts)}")
        print(f"Валидных постов: {len([p for p in posts if p.get('is_valid')])}")

        if posts:
            print(f"\n🎯 ПЕРВЫЕ 3 ПОСТА:")
            for i, post in enumerate(posts[:3]):
                print(f"\n--- Пост #{i + 1} ---")
                print(f"Заголовок: {post.get('title')}")
                print(f"URL: {post.get('source_url')}")
                print(f"Превью: {post.get('preview_content', '')[:80]}...")
                print(f"Текст: {len(post.get('original_content', ''))} символов")
                print(f"Изображение: {'Есть' if post.get('image_url') else 'Нет'}")
                print(f"Статус: {post.get('status', 'Не определен')}")
        else:
            print("❌ Посты не найдены!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_parser())
