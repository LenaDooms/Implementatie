class NotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class AlreadyExistsError(Exception):
    def __init__(self, message):
        self.message = message


class TypeNotMatchingError(Exception):
    def __init__(self, message):
        self.message = message
