# app/models/settings.py

from sqlalchemy import Column, Integer, String, Boolean
from .base import Base


class ImageModel(Base):
    __tablename__ = 'image_models'
    imageModelId = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "imageModelId": self.imageModelId,
            "name": self.name,
            "description": self.description,
            "disabled": self.disabled
        }


class DrawingStyle(Base):
    __tablename__ = 'drawing_styles'
    drawingStyleId = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    exampleImageUrl = Column(String, nullable=True)
    disabled = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "drawingStyleId": self.drawingStyleId,
            "name": self.name,
            "description": self.description,
            "exampleImageUrl": self.exampleImageUrl,
            "disabled": self.disabled
        }


class ColorBlindOption(Base):
    __tablename__ = 'colorblind_options'
    colorBlindOptionId = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    def to_dict(self):
        return {
            "colorBlindOptionId": self.colorBlindOptionId,
            "name": self.name,
            "description": self.description
        }