class InvalidHttpStatus(Exception):
    """Статут ответа от API Яндекс.Практикума отличный от 200."""

    pass


class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашнего задания."""

    pass


class KeyHomeworksIsInaccessible(Exception):
    """В ответе API Яндекс.Практикума отсутствует ключ 'homeworks'."""

    pass


class KeyHomeworkNameIsInaccessible(Exception):
    """В ответе API Яндекс.Практикума в словаре 'homeworks'.
    отсутствует ключ 'homework'.
    """

    pass


class KeyHomeworkStatusIsInaccessible(Exception):
    """В ответе API Яндекс.Практикума в словаре 'homeworks'.
    отсутствует ключ 'status'.
    """

    pass
