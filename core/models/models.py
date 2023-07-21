from sqlalchemy import Integer, ForeignKey, String, Column, DECIMAL
from core.models.base import BaseDBModel
from sqlalchemy.orm import relationship


class MenuDBModel(BaseDBModel):
    __tablename__ = 'menus'

    title = Column(String)
    description = Column(String)

    submenu = relationship("SubmenuDBModel", back_populates='menu', cascade="all, delete")


class SubmenuDBModel(BaseDBModel):
    __tablename__ = 'submenus'

    title = Column(String)
    description = Column(String)
    menu_id = Column(Integer, ForeignKey('menus.id', ondelete="CASCADE"), nullable=False)

    menu = relationship("MenuDBModel", foreign_keys=[menu_id], back_populates='submenu')
    dishes = relationship("DishDBModel", back_populates='submenus', cascade="all, delete")


class DishDBModel(BaseDBModel):
    __tablename__ = 'dishes'

    title = Column(String)
    description = Column(String)
    cost = Column(DECIMAL)

    submenus_id = Column(Integer, ForeignKey('submenus.id', ondelete="CASCADE"), nullable=False)
    submenus = relationship("SubmenuDBModel", foreign_keys=[submenus_id], back_populates='dishes')
