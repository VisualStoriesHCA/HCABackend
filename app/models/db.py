import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from ..models.achievements import Achievement
from ..models.base import Base
from ..models.settings import ImageModel, DrawingStyle, ColorBlindOption



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


async def load_settings_from_json():
    with open("/app/app/assets/settings/initial_settings.json", "r") as f:
        data = json.load(f)

    async with async_session() as session:
        # Load Image Models
        for model in data["imageModels"]:
            result = await session.execute(
                select(ImageModel).where(ImageModel.imageModelId == model["imageModelId"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            image_model = ImageModel(
                imageModelId=model["imageModelId"],
                name=model["name"],
                description=model["description"],
                disabled=model["disabled"]
            )
            session.add(image_model)

        # Load Drawing Styles
        for style in data["drawingStyles"]:
            result = await session.execute(
                select(DrawingStyle).where(DrawingStyle.drawingStyleId == style["drawingStyleId"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            drawing_style = DrawingStyle(
                drawingStyleId=style["drawingStyleId"],
                name=style["name"],
                description=style["description"],
                exampleImageUrl=style.get("exampleImageUrl"),
                disabled=style.get("disabled", False)
            )
            session.add(drawing_style)

        # Load ColorBlind Options
        for option in data["colorBlindOptions"]:
            result = await session.execute(
                select(ColorBlindOption).where(ColorBlindOption.colorBlindOptionId == option["colorBlindOptionId"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            colorblind_option = ColorBlindOption(
                colorBlindOptionId=option["colorBlindOptionId"],
                name=option["name"],
                description=option["description"]
            )
            session.add(colorblind_option)

        await session.commit()