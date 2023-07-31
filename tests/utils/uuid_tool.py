from uuid import UUID


def uuid_or_none(value):
    try:
        result = UUID(str(value))
    except ValueError:
        result = None
    return result
