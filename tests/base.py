from abc import ABC, abstractmethod
from typing import Generic

from httpx import Response

from tests.utils import CRUDDataBase, ModelType, reverse


class BaseTestCase(ABC, Generic[ModelType]):
    @property
    @abstractmethod
    def model(self):
        """DB model for asserting methods."""
        pass

    @property
    @abstractmethod
    def fields_for_assert(self):
        """List of fields  from DB model existing in response."""
        pass

    @staticmethod
    def reverse(name: str, **kwargs) -> str:
        """Generate API url by endpoint name"""
        return reverse(name, **kwargs)

    async def assert_equal_response_list_db_objects(
            self, resp_json_list: list[dict[str, str]], crud: CRUDDataBase
    ) -> None:
        """Assert for equaling between list of json objects and DB objects."""
        for resp_json in resp_json_list:
            target_obj: ModelType | None = await crud.get_by_id(self.model, resp_json['id'])
            assert target_obj is not None
            self.assert_resp_and_db_obj(resp_json, target_obj)

    async def assert_equal_response_db_object(
        self, response: Response, crud: CRUDDataBase, db_obj: ModelType | None = None
    ) -> None:
        """Assert for equaling between a response and a DB object."""
        resp_json: dict[str, str] = response.json()
        if db_obj is None:
            target_obj: ModelType | None = await crud.get_by_id(self.model, resp_json['id'])
        else:
            target_obj = db_obj

        assert target_obj is not None

        self.assert_resp_and_db_obj(resp_json, target_obj)

    def assert_resp_and_db_obj(self, resp_json: dict[str, str], db_obj: ModelType) -> None:
        """Assert for equaling between json and DB object."""
        for field in self.fields_for_assert:
            assert resp_json[field] == str(getattr(db_obj, field))

    @staticmethod
    def assert_payload_in_response(response: Response, **fields):
        """Assert for exist create/update payloads in response."""
        resp_json: dict[str, str] = response.json()
        if fields.get('price'):
            fields['price'] = '%.2f' % float(fields['price'])
        for field, value in fields.items():
            assert value == resp_json[field]
