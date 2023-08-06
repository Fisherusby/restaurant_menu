from typing import Any

from fastapi.routing import APIRoute

from core.endpoints.api import router


class ReverseError(Exception):
    pass


class NonExistReverseError(ReverseError):
    """
    Raised by reverse(name, args, kwargs, prefix)
    if router does not exist.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f'Router {name} does not exist')


class LotOfExistReverseError(ReverseError):
    """
    Raised by reverse(name, args, kwargs, prefix)
    if there are more than 1 routers.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f'Exist more than 1 routers with name {name}')


class BadArgsReverseError(ReverseError):
    """
    Raised by reverse(name, args)
    if router takes wrong count of arguments.
    """

    def __init__(self, name: str, take: int, given: int) -> None:
        super().__init__(f'Bad arguments: router {name} takes {take} argument but {given} were given')


class BadParamsReverseError(ReverseError):
    """
    Raised by reverse(name, kwargs)
    if router takes wrong named parameters.
    """

    def __init__(self, name: str, take_param_names: list[str], given_params: dict[str, Any] | None) -> None:
        take_param: str = ', '.join(take_param_names)
        if given_params is None:
            given_param: str = 'nothing'
        else:
            given_param = ', '.join(given_params.keys())
        super().__init__(f'Bad arguments: router {name} takes arguments: {take_param}, but were given {given_param}')


def reverse(name: str, *, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None, prefix: str = '') -> str:
    """Return url path for endpoint API by endpoint name."""
    routers = list(filter(lambda x: isinstance(x, APIRoute) and x.name == name, router.routes))
    if not routers:
        raise NonExistReverseError(name)

    if len(routers) > 1:
        raise LotOfExistReverseError(name)

    target_router = routers[0]
    param_names: list[str] = target_router.param_convertors.keys()
    if args is not None:
        if len(args) != len(target_router.param_convertors):
            raise BadArgsReverseError(name, len(param_names), len(args))
        params: dict[str, Any] = dict(zip(param_names, args))
    else:
        if (kwargs is not None and kwargs.keys() != param_names) or (kwargs is None and len(param_names) > 0):
            raise BadParamsReverseError(name, param_names, kwargs)
        params = kwargs if kwargs is not None else {}

    return f'{prefix}{target_router.path.format(**params)}'


def reverse_v1(name: str, **kwargs) -> str:
    """Generate API url by endpoint name"""
    return router.url_path_for(name, **kwargs)
