from sqlalchemy import DECIMAL, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models.base import BaseDBModel


class MenuDBModel(BaseDBModel):
    __tablename__ = 'menus'

    title = Column(String)
    description = Column(String)

    submenus = relationship('SubmenuDBModel', back_populates='menu', cascade='all, delete')


class SubmenuDBModel(BaseDBModel):
    __tablename__ = 'submenus'

    title = Column(String)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id', ondelete='CASCADE'), nullable=False)

    menu = relationship('MenuDBModel', foreign_keys=[menu_id], back_populates='submenus')
    dishes = relationship('DishDBModel', back_populates='submenu', cascade='all, delete')


class DishDBModel(BaseDBModel):
    __tablename__ = 'dishes'

    title = Column(String)
    description = Column(String)
    price = Column(DECIMAL(10, 2))
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenus.id', ondelete='CASCADE'), nullable=False)

    submenu = relationship('SubmenuDBModel', foreign_keys=[submenu_id], back_populates='dishes')
    discount = relationship('DiscountDBModel', back_populates='dish', uselist=False)


class DiscountDBModel(BaseDBModel):
    __tablename__ = 'dishes_discount'

    value = Column(DECIMAL(5, 2))
    dish_id = Column(UUID(as_uuid=True), ForeignKey('dishes.id', ondelete='CASCADE'), unique=True)

    dish = relationship('DishDBModel', back_populates='discount')
