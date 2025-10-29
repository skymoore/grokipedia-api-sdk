class GrokipediaError(Exception):
    pass


class GrokipediaAPIError(GrokipediaError):
    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class GrokipediaBadRequestError(GrokipediaAPIError):
    pass


class GrokipediaNotFoundError(GrokipediaAPIError):
    pass


class GrokipediaRateLimitError(GrokipediaAPIError):
    pass


class GrokipediaServerError(GrokipediaAPIError):
    pass


class GrokipediaNetworkError(GrokipediaError):
    pass


class GrokipediaValidationError(GrokipediaError):
    pass
