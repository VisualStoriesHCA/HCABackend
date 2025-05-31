import base64
import os
import re
from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict


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
    def __init__(self, image_id: str, image_url: str):
        self.id: str = image_id
        self.url: str = image_url
        self.alt: str = "no title sorry"

    def to_dict(self):
        return {
            "imageId": self.id,
            "url": self.url,
            "alt": self.alt
        }


class Story:
    def __init__(self, story_id: str, story_name: str, user_id: str):
        self.user_id = user_id
        self.id: str = story_id
        self.images: List[Image] = []
        self.coverage_image: str = "https://www.medien.ifi.lmu.de/team/rifat.amin/rifat_amin.jpg"
        self.last_edited: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.name: str = story_name
        self.text: str = "Type in your bootyful story bitch..."
        self._total_number_of_images_generated = 0

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
            "storyId": self.id,
            "storyName": self.name,
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

    def set_story_name(self, story_name):
        self.name = story_name

    def upload_image(self, image_binary: str):
        image_id = f"img_{self._total_number_of_images_generated}"
        self._total_number_of_images_generated += 1
        dir_path = f"/etc/images/{self.user_id}/{self.id}"
        os.makedirs(dir_path, exist_ok=True)
        match = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", image_binary)
        file_extension = match.group("ext")
        base64_data = match.group("data")
        with open(f"{dir_path}/{image_id}.{file_extension}", "wb") as img_file:
            img_file.write(base64.b64decode(base64_data))
        image_url = f"http://localhost:8080/images/{self.user_id}/{self.id}/{image_id}"
        self.images.append(Image(image_id=image_id, image_url=image_url))


class User:
    def __init__(self, name: str, user_name: str, user_id: str):
        self.id: str = user_id
        self.stories: OrderedDict[str, Story] = OrderedDict()
        self.account_created: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.name: str = name
        self.user_name: str = user_name
        self._total_number_of_stories_generated: int = 0

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

    def create_story(self, story_name: str) -> str:
        story_id = f"s_{self._total_number_of_stories_generated}"
        self._total_number_of_stories_generated += 1
        self.stories[story_id] = Story(story_name=story_name, story_id=story_id, user_id=self.id)
        return story_id

    def delete_story(self, story_id: str) -> bool:
        if story_id in self.stories:
            del self.stories[story_id]
            return True
        return False

    def get_stories(self, max_entries: int = 1) -> List[Story]:
        return list(self.stories.values())[:max_entries]

    def get_story(self, story_id: str) -> Story:
        return self.stories[story_id]
