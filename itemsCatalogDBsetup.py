# Configuration
# Imports needed modules & creates an instance of Declarative Base Class
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()

# Class and Mappers
# Representation of a table as a python class
# Extends the Base Class nested inside table & maper code


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    # Configured with cascading deletion
    items = relationship('Item', cascade='all, delete-orphan')

    @property
    def serializeCategories(self):
        # Returns object data in easily serializable format
        return {
            'id' : self.id,
            'name' : self.name,
        }


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('categories.id'))

    # Configured with cascading deletion
    categories = relationship('Category', cascade='save-update')


    @property
    def serializeItems(self):
        # Returns object data in easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id
        }





engine = create_engine('sqlite:///itemsCatalog.db')
Base.metadata.create_all(engine)

