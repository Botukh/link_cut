from http import HTTPStatus


class ValidationError(Exception):
    """Базовое исключение для операций валидации"""
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIError(Exception):
    """Исключение для API операций"""
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)