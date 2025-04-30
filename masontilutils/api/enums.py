from enum import Enum


class APIResponse(Enum):
    REJECTED = 1
    FOUND = 2
    NONE = 3
    ERROR = 4