import base64
import os
import re
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict

from sqlalchemy import Integer, select, update
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Enum as SqlEnum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from ..models.db import Base


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
        image_operation = ImageOperation(operation=Operation.parse_operation(image_operation_dict["type"]),
                                         image_id=image_operation_dict["imageId"],
                                         canvas_data=image_operation_dict["canvasData"],
                                         alt=image_operation_dict["alt"])
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


class Story(Base):
    __tablename__ = "stories"
    storyId = Column(String, primary_key=True)
    name = Column(String)
    text = Column(Text, default="Type in your creative story...")
    coverageImage = Column(String, default="http://localhost:8080/assets/logos/new_story")
    lastEdited = Column(String, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    userId = Column(String, ForeignKey('users.userId'))
    image_counter = Column(Integer, default=0)

    images = relationship("Image", backref="story", cascade="all, delete-orphan")

    # --- Methods ---

    def to_dict(self):
        return {
            "storyId": self.storyId,
            "coverImage": self.CoverageImage,
            "storyName": self.name,
            "lastEdited": self.lastEdited,
            "storyText": self.text,
            "storyImages": reversed([image.to_dict() for image in self.images])
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
            "storyText": self.text,
            "storyImages": reversed([image.to_dict() for image in self.images])
        }

    def set_text(self, updated_text: str):
        self.text = updated_text
        self.lastEdited = datetime.now(timezone.utc)

    def update_images_by_text(self):
        # placeholder: implement your actual logic here
        pass

    def update_text_by_images(self):
        # placeholder: implement your actual logic here
        pass

    def update_from_image_operations(self, image_operations: List[Dict]):
        operations = [ImageOperation.parse_image_operation(op) for op in image_operations]
        self.set_text("new text")  # Placeholder logic

    def set_story_name(self, story_name: str):
        self.name = story_name
        self.lastEdited = datetime.now(timezone.utc)

    def upload_image(self, image_binary: str):
        self.image_counter +=1
        image_id = f"img_{self.storyId}_{self.image_counter}"
        dir_path = f"/etc/images/{self.userId}/{self.storyId}"
        os.makedirs(dir_path, exist_ok=True)

        match = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", image_binary)
        if not match:
            raise ValueError("Invalid image binary format")

        file_extension = match.group("ext")
        base64_data = match.group("data")

        image_filename = f"{image_id}.{file_extension}"
        with open(os.path.join(dir_path, image_filename), "wb") as img_file:
            img_file.write(base64.b64decode(base64_data))

        image_url = f"http://localhost:8080/images/{self.userId}/{self.storyId}/{image_id}"
        new_image = Image(imageId=image_id, url=image_url, storyId=self.storyId)

        self.images.append(new_image)
        self.lastEdited = datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'
    userId = Column(String, primary_key=True)
    name = Column(String)
    userName = Column(String)
    accountCreated = Column(String, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    story_counter = Column(Integer, default=0)
    stories = relationship("Story", backref="user", cascade="all, delete-orphan")

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
