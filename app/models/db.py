import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from ..models.achievements import Achievement
from ..models.base import Base

engine = create_async_engine('sqlite+aiosqlite:///data/app.db', echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def load_achievements_from_json():
    with open("/app/app/assets/achievements/achievements.json", "r") as f:
        data = json.load(f)["achievements"]

    async with async_session() as session:
        for ach in data:
            result = await session.execute(
                select(Achievement).where(Achievement.achievementId == ach["achievementId"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            base = Achievement(
                achievementId=ach["achievementId"],
                title=ach["title"],
                description=ach["description"],
                category=ach["category"],
                type=ach["type"],
                imageUrl=ach["imageUrl"],
                targetValue=ach["targetValue"],
                unit=ach["unit"],
                reward_points=ach["reward"]["points"],
                reward_badge=ach["reward"]["badge"],
                unlockCondition=ach.get("unlockCondition")
            )
            session.add(base)

        await session.commit()
