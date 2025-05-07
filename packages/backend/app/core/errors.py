class AppError(Exception):
    def __init__(self, message: str | None = None):
        if message is None:
            message = self.__class__.__name__
        super().__init__(message)
        self.message = message


class LockedError(AppError):
    message = "Locked"
