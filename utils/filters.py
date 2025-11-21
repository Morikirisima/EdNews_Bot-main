import re
import config


# Проверка текста на наличие рекламы
def is_advertisement_content(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    ad_words_count = 0
    for word in config.AD_FILTER_WORDS:
        if word in text_lower:
            ad_words_count += 1

    if ad_words_count >= config.MAX_AD_WORDS_COUNT:
        return True

    ad_patterns_count = 0
    for pattern in config.AD_FILTER_PATTERNS:
        if re.search(pattern, text_lower):
            ad_patterns_count += 1

    if ad_words_count > 0 and ad_patterns_count >= 2:
        return True

    total_ad_signals = ad_words_count + ad_patterns_count
    if total_ad_signals >=3:
        return True

    return False


# Определяет надобность ручной проверки админом
def needs_manual_review(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    for word in config.MANUAL_REVIEW_WORDS:
        if word in text_lower:
            return True

    if len(text) > config.MAX_AUTO_POST_LENGTH:
        return True

    return False
