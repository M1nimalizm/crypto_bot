def get_username_or_request(user):
    """
    Возвращает @username пользователя, если он есть,
    иначе — его Telegram ID в формате "ID: 123456789"
    """
    if user.username:
        return f"@{user.username}"
    return f"ID: {user.id}"

def parse_ref(args):
    """
    Возвращает реферальный код, если передан с /start,
    иначе — "без ссылки"
    """
    return args if args else "без ссылки"
