import base64
import logging
import os
import re
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import List, Dict

from PIL import Image as PIL_Image
from openai import AsyncOpenAI
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy import Integer, Boolean, select, Enum as SQLAlchemyEnum, and_
from sqlalchemy.orm import relationship

from ..models import utils
from ..models.achievements import Achievement
from ..models.base import Base
from ..routers.schemas import StoryState, AchievementState

logger = logging.getLogger(__name__)


class Operation(Enum):
    NO_CHANGE = 1
    SKETCH_FROM_SCRATCH = 2
    SKETCH_ON_IMAGE = 3

    @staticmethod
    def parse_operation(operation: str) -> "Operation":
        match operation.lower().strip():
            case "nochange":
                return Operation.NO_CHANGE
            case "sketchfromscratch":
                return Operation.SKETCH_FROM_SCRATCH
            case "sketchonimage":
                return Operation.SKETCH_ON_IMAGE
            case _:
                raise Exception(f"Unknown operation {operation}")


class ImageOperation:
    def __init__(self, operation: Operation, image_id: str = None, canvas_data: str = None, alt: str = None):
        self.operation = operation
        self.image_id = image_id
        self.canvas_data = canvas_data
        self.alt = alt

    @staticmethod
    def parse_image_operation(image_operation_dict: dict) -> "ImageOperation":
        operation = Operation.parse_operation(image_operation_dict["type"])
        image_operation = ImageOperation(operation)
        match operation:
            case Operation.NO_CHANGE:
                image_operation.image_id = image_operation_dict["imageId"]
            case Operation.SKETCH_FROM_SCRATCH:
                image_operation.canvas_data = image_operation_dict["canvasData"]
            case Operation.SKETCH_ON_IMAGE:
                image_operation.image_id = image_operation_dict["imageId"]
                image_operation.canvas_data = image_operation_dict["canvasData"]
            case _:
                raise Exception(f"Unknown operation {operation}")
        return image_operation


class Image(Base):
    __tablename__ = 'images'
    imageId = Column(String, primary_key=True)
    url = Column(String)
    alt = Column(String, default="no title sorry")
    storyId = Column(String, ForeignKey('stories.storyId'))

    def to_dict(self):
        return {
            "imageId": self.imageId,
            "url": self.url,
            "alt": self.alt
        }


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String, ForeignKey('users.userId'))
    achievementId = Column(String, ForeignKey('achievements.achievementId'))

    state = Column(SQLAlchemyEnum(AchievementState), default=AchievementState.locked)
    currentValue = Column(Integer, default=0)
    completedAt = Column(DateTime, nullable=True)
    lastUpdate = Column(DateTime, nullable=True)

    achievement = relationship("Achievement", lazy="selectin")

    def to_dict(self):
        return {
            "achievementId": int(self.achievementId),
            "title": self.achievement.title if self.achievement else None,
            "description": self.achievement.description if self.achievement else None,
            "category": self.achievement.category if self.achievement else None,
            "type": self.achievement.type if self.achievement else None,
            "imageUrl": self.achievement.imageUrl if self.achievement else None,
            "state": self.state.name if self.state else None,
            "currentValue": self.currentValue,
            "targetValue": self.achievement.targetValue if self.achievement else None,
            "unit": self.achievement.unit if self.achievement else None,
            "completedAt": self.completedAt.isoformat() if self.completedAt else None,
            "reward": {
                "points": self.achievement.reward_points if self.achievement else None,
                "badge": self.achievement.reward_badge if self.achievement else None,
            },
            "unlockCondition": self.achievement.unlockCondition if self.achievement else None,
        }


class Story(Base):
    __tablename__ = "stories"
    storyId = Column(String, primary_key=True)
    name = Column(String)
    text = Column(Text, default="")
    coverageImage = Column(String, default="http://localhost:8080/assets/logos/new_story")
    lastEdited = Column(String, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    userId = Column(String, ForeignKey('users.userId'))
    image_counter = Column(Integer, default=0)
    state = Column(SQLAlchemyEnum(StoryState), default=StoryState.completed, nullable=False)
    audio_counter = Column(Integer, default=0)
    audio = Column(Text, default=None, nullable=True)

    imageModelId = Column(Integer, ForeignKey('image_models.imageModelId'), default=1)
    drawingStyleId = Column(Integer, ForeignKey('drawing_styles.drawingStyleId'), default=2)
    colorBlindOptionId = Column(Integer, ForeignKey('colorblind_options.colorBlindOptionId'), default=1)
    regenerateImage = Column(Boolean, default=True)

    images = relationship("Image", backref="story", cascade="all, delete-orphan", lazy="selectin")

    imageModel = relationship("ImageModel", lazy="selectin")
    drawingStyle = relationship("DrawingStyle", lazy="selectin")
    colorBlindOption = relationship("ColorBlindOption", lazy="selectin")

    # --- Methods ---

    def to_dict(self):
        return {
            "storyId": self.storyId,
            "coverImage": self.coverageImage,
            "storyName": self.name,
            "lastEdited": self.lastEdited,
            "storyText": self.get_formatted_text(),
            "state": self.state.value,
            "storyImages": list(reversed([image.to_dict() for image in self.images])),
            "audioUrl": self.audio,
            "settings": {
                "imageModelId": self.imageModelId,
                "drawingStyleId": self.drawingStyleId,
                "colorBlindOptionId": self.colorBlindOptionId,
                "regenerateImage": self.regenerateImage
            }
        }

    def to_story_basic_information(self):
        return {
            "storyId": self.storyId,
            "coverImage": self.coverageImage,
            "storyName": self.name,
            "lastEdited": self.lastEdited
        }

    def to_story_details_response(self):
        return {
            "storyId": self.storyId,
            "storyName": self.name,
            "storyText": self.get_formatted_text(),
            "state": self.state.value,
            "storyImages": list(reversed([image.to_dict() for image in self.images])),
            "audioUrl": self.audio,
            "settings": {
                "imageModelId": self.imageModelId,
                "drawingStyleId": self.drawingStyleId,
                "colorBlindOptionId": self.colorBlindOptionId,
                "regenerateImage": self.regenerateImage
            }
        }

    def get_raw_text(self) -> str:
        return utils.get_raw_text(self.text)

    def get_formatted_text(self) -> str:
        return self.text

    def set_raw_text(self, updated_text: str):
        updated_text = utils.get_raw_text(updated_text)
        self.text = updated_text
        self.lastEdited = datetime.now(timezone.utc)

    def set_formatted_text(self, updated_text: str):
        raw_text = self.get_raw_text()
        updated_text = utils.get_raw_text(updated_text)
        if raw_text:
            updated_text = utils.highlight_additions(raw_text, updated_text)
        self.text = updated_text
        self.lastEdited = datetime.now(timezone.utc)

    def update_state(self, state: StoryState):
        self.state = state

    def update_settings(self, imageModelId=None, drawingStyleId=None, colorBlindOptionId=None, regenerateImage=None):
        if imageModelId is not None:
            self.imageModelId = imageModelId
        if drawingStyleId is not None:
            self.drawingStyleId = drawingStyleId
        if colorBlindOptionId is not None:
            self.colorBlindOptionId = colorBlindOptionId
        if regenerateImage is not None:
            self.regenerateImage = regenerateImage
        self.lastEdited = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    async def update_images_by_text(self, new_text: str):
        self.set_raw_text(new_text)
        self.audio = None
        logger.debug(f"Story text: {self.text}")
        raw_text = self.get_raw_text()
        base64_image = await self.modify_image_from_text(raw_text)
        await self.upload_image(base64_image)
        await self.update_story_name()

    async def update_from_image_operations(self, image_operations: List[Dict]):
        operations = [ImageOperation.parse_image_operation(op) for op in image_operations]
        await self.execute_image_operations(operations)
        await self.update_story_name()

    def set_story_name(self, story_name: str):
        self.name = story_name
        self.lastEdited = datetime.now(timezone.utc)

    async def update_story_name(self):
        if self.name == "New Story":
            client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
            image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-1].imageId}.png"
            from ..models.openai_client import image_to_title
            story_title = await image_to_title(client, image_path)
            self.name = story_title

    async def upload_image(self, image_binary: str):
        logger.debug(f"Calling `upload_image`...")
        self.image_counter += 1
        image_id = f"img_{self.storyId}_{self.image_counter}"
        dir_path = f"/etc/images/{self.userId}/{self.storyId}"
        os.makedirs(dir_path, exist_ok=True)

        match = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", image_binary)
        if not match:
            raise ValueError("Invalid image binary format")

        file_extension = match.group("ext").lower()
        base64_data = match.group("data")

        # Validate file extension
        if file_extension not in ['jpeg', 'jpg', 'png']:
            raise ValueError(
                f"Unsupported image format: {file_extension}. Only JPEG, JPG, and PNG formats are supported.")

        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        image_filename = f"{image_id}.png"

        # Convert JPEG to PNG if needed, otherwise keep as is
        if file_extension in ['jpeg', 'jpg']:
            # Convert JPEG to PNG using PIL
            from io import BytesIO
            image = PIL_Image.open(BytesIO(image_data))
            # Convert to RGB if necessary (in case of RGBA)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')

            # Save as PNG
            image_path = os.path.join(dir_path, image_filename)
            image.save(image_path, 'PNG')
        else:
            # For PNG and other formats, save as is but ensure PNG extension
            with open(os.path.join(dir_path, image_filename), "wb") as img_file:
                img_file.write(image_data)

        image_url = f"http://localhost:8080/images/{self.userId}/{self.storyId}/{image_id}"
        new_image = Image(imageId=image_id, url=image_url, storyId=self.storyId)

        self.images.append(new_image)
        self.lastEdited = datetime.now(timezone.utc)
        logger.debug(f"Image was successfully uploaded.")

    async def generate_audio(self, text: str):
        new_raw_text = utils.get_raw_text(text)
        if self.audio and new_raw_text == self.get_raw_text():
            return
        self.set_raw_text(new_raw_text)
        self.audio_counter += 1
        audio_id = f"aud_{self.storyId}_{self.audio_counter}"
        dir_path = f"/etc/audio/{self.userId}/{self.storyId}"
        os.makedirs(dir_path, exist_ok=True)
        audio_filename = f"{audio_id}.wav"
        from ..models.openai_client import text_to_speech
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
        audio_wav = await text_to_speech(client, new_raw_text)
        with open(os.path.join(dir_path, audio_filename), "wb") as audio_file:
            audio_file.write(audio_wav)
        self.lastEdited = datetime.now(timezone.utc)
        self.audio = f"http://localhost:8080/audio/{self.userId}/{self.storyId}/{audio_id}"

    async def execute_image_operation(self, image_operation: ImageOperation):
        logger.debug(f"Calling `execute_image_operation` with operation {image_operation.operation}")
        match image_operation.operation:
            case Operation.NO_CHANGE:
                logger.debug(f"Operation {Operation.NO_CHANGE}")
                new_text = await self.generate_no_change_text_string()
                self.set_formatted_text(new_text)
                self.audio = None
            case Operation.SKETCH_FROM_SCRATCH:
                logger.debug(f"Operation {Operation.SKETCH_FROM_SCRATCH}")
                await self.upload_image(image_operation.canvas_data)

                # Only generate new image if regenerateImage is True
                logger.debug(f"`regenerateImage` is set to {self.regenerateImage}")
                if self.regenerateImage:
                    base64_image = await self.generate_image_sketch_from_scratch()
                    await self.upload_image(base64_image)

                new_text = await self.generate_no_change_text_string()
                self.set_formatted_text(new_text)
                self.audio = None
            case Operation.SKETCH_ON_IMAGE:
                logger.debug(f"Operation {Operation.SKETCH_ON_IMAGE}")
                await self.upload_image(image_operation.canvas_data)

                # Only generate new image if regenerateImage is True
                if self.regenerateImage:
                    base64_image = await self.generate_image_sketch_on_image()
                    await self.upload_image(base64_image)

                new_text = await self.generate_no_change_text_string()
                self.set_formatted_text(new_text)
                self.audio = None
            case _:
                raise Exception(f"Unknown operation {image_operation.operation}")

    async def execute_image_operations(self, image_operations: List[ImageOperation]):
        for image_operation in image_operations:
            await self.execute_image_operation(image_operation)

    async def generate_no_change_text_string(self):
        logger.debug("Calling 'generate_no_change_text_string'")
        logger.debug(f"Creating OpenAI client...")
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
        image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-1].imageId}.png"
        from ..models.openai_client import image_to_story
        original_text = self.get_raw_text()
        logger.debug("Calling 'image_to_story'")
        return await image_to_story(client, image_path, original_text)

    async def generate_image_sketch_from_scratch(self) -> str:
        logger.debug("Calling 'generate_image_sketch_from_scratch'")
        logger.debug(f"Creating OpenAI client...")
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
        logger.debug(f"OpenAI client created successfully!")
        from ..models.openai_client import modify_image
        image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-1].imageId}.png"
        logger.debug("Calling 'modify_image'")
        return await modify_image(client, image_path, None, self.drawingStyleId, self.colorBlindOptionId)

    async def generate_image_sketch_on_image(self) -> str:
        logger.debug("Calling 'generate_image_sketch_on_image'")
        logger.debug(f"Creating OpenAI client...")
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
        from ..models.openai_client import sketch_on_image
        previous_image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-2].imageId}.png"
        image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-1].imageId}.png"
        original_text = self.get_raw_text()
        logger.debug("Calling 'sketch_on_image'")
        logger.debug(f"Story: {original_text}")
        return await sketch_on_image(client,
                                     image_path,
                                     previous_image_path,
                                     original_text,
                                     self.drawingStyleId,
                                     self.colorBlindOptionId,
                                     )

    async def modify_image_from_text(self, text="") -> str:
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
        from ..models.openai_client import modify_image, story_to_image
        from pathlib import Path
        file_path = None
        if self.images:
            image_path = f"/etc/images/{self.userId}/{self.storyId}/{self.images[-1].imageId}.png"
            file_path = Path(image_path)

        if file_path and file_path.exists():
            return await modify_image(client, image_path, text, self.drawingStyleId, self.colorBlindOptionId)
        else:
            return await story_to_image(client, text, self.drawingStyleId, self.colorBlindOptionId)


class User(Base):
    __tablename__ = 'users'
    userId = Column(String, primary_key=True)
    name = Column(String)
    userName = Column(String)
    accountCreated = Column(String, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    story_counter = Column(Integer, default=0)
    stories = relationship("Story", backref="user", cascade="all, delete-orphan", lazy="selectin")
    achievements = relationship("UserAchievement", cascade="all, delete-orphan", lazy="selectin")

    def __str__(self):
        return f"Id: {self.userId}\nName: {self.name}\nUsername: {self.userName}\nAccount Created: {self.accountCreated}"

    def to_dict(self):
        return {
            "userId": self.userId,
            "name": self.name,
            "userName": self.userName,
            "accountCreated": self.accountCreated
        }

    def create_story(self, story_name: str) -> str:
        self.story_counter += 1
        storyId = f"s_{self.userId}_{self.story_counter}"
        story = Story(storyId=storyId, name=story_name, userId=self.userId)
        return story

    def get_stories(self, max_entries: int = 1):
        return self.stories[:max_entries]

    def get_story(self, storyId: str) -> Story:
        for s in self.stories:
            if s.storyId == storyId:
                return s
        raise ValueError("Story not found")

    async def get_achievements(self, db):
        base_achievements = await db.scalars(select(Achievement))
        base_achievements = base_achievements.all()
        user_achievements_map = {ua.achievementId: ua for ua in self.achievements}

        result = []

        for base_ach in base_achievements:
            if base_ach.achievementId in user_achievements_map.keys():
                user_ach = user_achievements_map[base_ach.achievementId]
                if not user_ach.achievement:
                    user_ach.achievement = base_ach
                result.append(user_ach.to_dict())
            else:
                virtual_ua = UserAchievement(
                    userId=self.userId,
                    achievementId=base_ach.achievementId,
                    state=AchievementState.locked,
                    currentValue=0,
                    completedAt=None,
                    achievement=base_ach,
                    lastUpdate=None
                )
                result.append(virtual_ua.to_dict())

        return {"achievements": result}

    async def update_achievement(self, achievementId: str, db, story=None):
        async def get_achievement(achievement_id):
            base_ach = await db.scalar(select(Achievement).where(Achievement.achievementId == achievement_id))
            if not base_ach:
                raise ValueError(f"Achievement {achievement_id} not found")
            result = await db.execute(
                select(UserAchievement)
                .where(
                    and_(
                        UserAchievement.userId == self.userId,
                        UserAchievement.achievementId == achievement_id
                    )
                )
            )
            user_ach = result.scalar_one_or_none()
            return base_ach, user_ach

        base_ach, user_ach = await get_achievement(achievementId)
        current_time = datetime.now(timezone.utc)
        match achievementId:
            case "1":
                if user_ach is None:
                    user_ach = UserAchievement(
                        userId=self.userId,
                        achievementId=achievementId,
                        state=AchievementState.in_progress,
                        currentValue=1,
                        completedAt=None,
                        achievement=base_ach,
                        lastUpdate=current_time
                    )
                else:
                    user_ach.currentValue += 1
                    user_ach.lastUpdate = current_time
                    if user_ach.currentValue >= 10:
                        user_ach.state = AchievementState.completed
                        user_ach.completedAt = current_time
                        _, user_ach_4 = await get_achievement("4")
                        if user_ach_4 is not None and user_ach_4.currentValue >= 7:
                            user_ach_4.state = AchievementState.completed
                            user_ach_4.completedAt = current_time

            case "2":
                number_words = len(story.get_raw_text().replace("<br>", "").strip().replace(" ", ""))
                if user_ach is None:
                    user_ach = UserAchievement(
                        userId=self.userId,
                        achievementId=achievementId,
                        state=AchievementState.in_progress,
                        currentValue=number_words,
                        completedAt=None,
                        achievement=base_ach,
                        lastUpdate=current_time
                    )
                else:
                    user_ach.currentValue = max(user_ach.currentValue, number_words)
                    user_ach.lastUpdate = current_time
                    if user_ach.currentValue >= 1000:
                        user_ach.state = AchievementState.completed
                        user_ach.completedAt = current_time

            case "3":
                if user_ach is None:
                    user_ach = UserAchievement(
                        userId=self.userId,
                        achievementId=achievementId,
                        state=AchievementState.in_progress,
                        currentValue=1,
                        completedAt=None,
                        achievement=base_ach,
                        lastUpdate=current_time
                    )
                else:
                    user_ach.currentValue += 1
                    user_ach.lastUpdate = current_time
                    if user_ach.currentValue >= 25:
                        user_ach.state = AchievementState.completed
                        user_ach.completedAt = current_time
            case "4":
                if user_ach is None:
                    user_ach = UserAchievement(
                        userId=self.userId,
                        achievementId=achievementId,
                        state=AchievementState.in_progress,
                        currentValue=1,
                        completedAt=None,
                        achievement=base_ach,
                        lastUpdate=current_time
                    )
                else:
                    if user_ach.lastUpdate.tzinfo is None:
                        user_ach.lastUpdate = user_ach.lastUpdate.replace(tzinfo=timezone.utc)
                    delta = current_time - user_ach.lastUpdate
                    if delta >= timedelta(minutes=1):
                        user_ach.currentValue += 1
                        user_ach.lastUpdate = current_time
                    if user_ach.currentValue >= 7:
                        # check for unlock condition for 1
                        _, user_ach_1 = await get_achievement("1")
                        if user_ach_1.state == AchievementState.completed:
                            user_ach.state = AchievementState.completed
                            user_ach.completedAt = current_time

        return user_ach
