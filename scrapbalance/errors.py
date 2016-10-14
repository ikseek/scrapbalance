from re import compile as regex


class NotLoggedIn(RuntimeError):
    pass


class UnexpectedResponse(Exception):
    pass


class BadRequest(Exception):
    ERROR_REGEX = regex(r'')

    @classmethod
    def from_error_text(cls, error_text):
        for subclass in cls.__subclasses__():
            instance = subclass.from_error_text(error_text)
            if instance:
                return instance
        if cls.ERROR_REGEX.match(error_text):
            return cls(error_text)


class BadLogin(BadRequest):
    ERROR_REGEX = regex(r'Введен неизвестный номер телефона')


class BadPassword(BadRequest):
    ERROR_REGEX = regex(r'Введен неверный пароль')


class AccessBlocked(BadRequest):
    ERROR_REGEX = regex(r'Доступ к Интернет-Помощнику заблокирован')
