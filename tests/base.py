from abc import ABC, abstractmethod
from typing import Dict, Optional

from httpx import AsyncClient, Response

from tests.utils.crud import CRUDDataBase, ModelType


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
        self, response: Response, crud: CRUDDataBase, db_obj: Optional[ModelType] = None
    ):
        """Assert for equaling between response and DB object."""
        resp_json: Dict[str, str] = response.json()
        if db_obj is None:
            db_obj: Optional[ModelType] = await crud.get_by_id(self.model, resp_json['id'])
        assert db_obj is not None

        for field in self.fields_for_assert:
            assert resp_json[field] == str(getattr(db_obj, field))

    @staticmethod
    def assert_payload_in_response(response: Response, **fields):
        """Assert for exist create/update payloads in response."""
        resp_json: Dict[str, str] = response.json()
        if fields.get('price'):
            fields['price']: str = "%.2f" % float(fields['price'])
        for field, value in fields.items():
            assert value == resp_json[field]
