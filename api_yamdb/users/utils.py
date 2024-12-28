import random
import string


def generate_confirmation_code(length=6):
    """
    Генерирует случайный цифровой код подтверждения заданной длины.
    По умолчанию длина кода — 6 символов.
    """
    return ''.join(random.choices(string.digits, k=length))
