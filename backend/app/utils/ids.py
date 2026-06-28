from uuid import NAMESPACE_URL, uuid5


def stable_id(value: str) -> str:
    return str(uuid5(NAMESPACE_URL, value))
