from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict


class Operation(Enum):
    KEEP = 1
    REMOVE = 2
    MODIFY = 3
    ADD = 4

    @staticmethod
    def parse_operation(operation: str) -> "Operation":
        match operation.lower().strip():
            case "KEEP":
                return Operation.KEEP
            case "REMOVE":
                return Operation.REMOVE
            case "MODIFY":
                return Operation.MODIFY
            case "ADD":
                return Operation.ADD
            case _:
                raise Exception(f"Unknown operation {operation}")


class ImageOperation:
    def __init__(self, operation: Operation, image_id: str, canvas_data: str, alt: str = None):
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


class Image:
    def __init__(self, imageId: str):
        self.id: str = imageId
        self.url: str = ""
        self.alt: str = ""

    def to_dict(self):
        return {
            "imageId": self.id,
            "url": self.url,
            "alt": self.alt
        }


class Story:
    def __init__(self, story_id: str):
        self.id: str = story_id
        self.images: List[Image] = []
        self.coverage_image: str = ""
        self.last_edited: str = ""
        self.name: str = ""
        self.text: str = ""

    def to_dict(self):
        return {
            "storyId": self.id,
            "coverImage": self.coverage_image,
            "storyName": self.name,
            "lastEdited": self.last_edited,
            "storyText": self.text,
            "storyImages": [image.to_dict() for image in self.images]
        }

    def to_story_basic_information(self):
        return {
            "storyId": self.id,
            "coverImage": self.coverage_image,
            "storyName": self.name,
            "lastEdited": self.last_edited
        }

    def to_story_details_response(self):
        return {
            "storyText": self.text,
            "storyImages": [image.to_dict() for image in self.images]
        }

    def set_text(self, updated_text: str):
        self.text = updated_text

    def update_images_by_text(self):
        pass

    def update_text_by_images(self):
        pass

    def update_from_image_operations(self, image_operations: List[Dict]):
        operations = [ImageOperation.parse_image_operation(image_operation) for image_operation in image_operations]
        self.set_text("new text")


class User:
    def __init__(self, name: str, user_name: str, user_id: str):
        self.id: str = user_id
        self.stories: OrderedDict[str, Story] = OrderedDict()
        self.account_created: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.name: str = name
        self.user_name: str = user_name

    def __str__(self):
        buffer = ""
        buffer += "Id:              " + self.id + "\n"
        buffer += "Name:            " + self.name + "\n"
        buffer += "Username:        " + self.user_name + "\n"
        buffer += "Account Created: " + self.account_created + "\n"
        return buffer

    def to_dict(self):
        return {
            "userId": self.id,
            "name": self.name,
            "userName": self.user_name,
            "accountCreated": self.account_created
        }

    def get_stories(self, max_entries: int = 1) -> List[Story]:
        return list(self.stories.values())[:max_entries]

    def get_story(self, story_id: str) -> Story:
        return self.stories[story_id]
