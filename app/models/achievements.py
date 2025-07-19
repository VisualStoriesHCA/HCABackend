# models.py

import logging

from openai import AsyncOpenAI
from sqlalchemy import Column, String, Text
from sqlalchemy import Integer

from ..models.base import Base

logger = logging.getLogger(__name__)


class Achievement(Base):
    __tablename__ = "achievements"
    achievementId = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    type = Column(String)
    imageUrl = Column(String)
    targetValue = Column(Integer)
    unit = Column(String)
    reward_points = Column(Integer)
    reward_badge = Column(String)
    unlockCondition = Column(String, nullable=True)
