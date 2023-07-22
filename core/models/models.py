from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.models.base import BaseDBModel


class MenuDBModel(BaseDBModel):
    __tablename__ = 'menus'

    title = Column(String)
    description = Column(String)

    submenus = relationship("SubmenuDBModel", back_populates='menu', cascade="all, delete")


class SubmenuDBModel(BaseDBModel):
    __tablename__ = 'submenus'

    title = Column(String)
    description = Column(String)
    menu_id = Column(Integer, ForeignKey('menus.id', ondelete="CASCADE"), nullable=False)

    menu = relationship("MenuDBModel", foreign_keys=[menu_id], back_populates='submenus')
    dishes = relationship("DishDBModel", back_populates='submenu', cascade="all, delete")


class DishDBModel(BaseDBModel):
    __tablename__ = 'dishes'

    title = Column(String)
    description = Column(String)
    price = Column(DECIMAL(10, 2))
    submenu_id = Column(Integer, ForeignKey('submenus.id', ondelete="CASCADE"), nullable=False)

    submenu = relationship("SubmenuDBModel", foreign_keys=[submenu_id], back_populates='dishes')

    # flake8: noqa: A003
    def to_dict(self):
        result = super().to_dict()
        if result.get('price'):
            result['price'] = str(result['price'])
        return result
