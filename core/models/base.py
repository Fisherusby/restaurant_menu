from sqlalchemy import Integer, Column
from sqlalchemy.orm import as_declarative


@as_declarative()
class BaseDBModel:
    id = Column(Integer, primary_key=True, index=True)
    __name__: str

    def dict(self):
        result = self.__dict__
        result['id'] = str(result['id'])
        return result
