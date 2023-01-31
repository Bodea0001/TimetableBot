class FailedTokenRefresh(Exception):
    pass


class UnknownTokenType(Exception):
    pass


class UnknownUser(Exception):
    pass


class EmptyResponse(Exception):
    pass


class NotOkResponse(Exception):
    pass