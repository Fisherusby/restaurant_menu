from sqlalchemy import Column, Integer
from sqlalchemy.orm import as_declarative


@as_declarative()
class BaseDBModel:
    # flake8: noqa: A003
    id = Column(Integer, primary_key=True, index=True)
    __name__: str

    # flake8: noqa: A003
    def dict(self):
        result = self.__dict__
        result['id'] = str(result['id'])
        return result
