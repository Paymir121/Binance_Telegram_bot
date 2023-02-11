class NotSendmessageException(Exception):
    """Не отправилось сообщение."""
    pass


class OurRequestError(Exception):
    """Ошибка запроса."""
    pass