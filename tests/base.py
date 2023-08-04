from abc import ABC, abstractmethod

from httpx import Response

from tests.utils import CRUDDataBase, ModelType


class BaseTestCase(ABC):
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

    async def assert_equal_response_db_object(
        self, response: Response, crud: CRUDDataBase, db_obj: ModelType | None = None
    ):
        """Assert for equaling between response and DB object."""
        resp_json: dict[str, str] = response.json()
        if db_obj is None:
            target_obj: ModelType | None = await crud.get_by_id(self.model, resp_json['id'])
        else:
            target_obj = db_obj

        assert target_obj is not None

        for field in self.fields_for_assert:
            assert resp_json[field] == str(getattr(target_obj, field))

    @staticmethod
    def assert_payload_in_response(response: Response, **fields):
        """Assert for exist create/update payloads in response."""
        resp_json: dict[str, str] = response.json()
        if fields.get('price'):
            fields['price'] = '%.2f' % float(fields['price'])
        for field, value in fields.items():
            assert value == resp_json[field]
