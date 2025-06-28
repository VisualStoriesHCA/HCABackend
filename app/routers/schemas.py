from enum import Enum
from typing import Optional, List, Union, Literal

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


# Image Operation Models
class NoChangeOperation(BaseModel):
    type: Literal["nochange"]
    imageId: str = Field(..., description="Id of the existing image", example="img_891415125124_1")


class SketchFromScratchOperation(BaseModel):
    type: Literal["sketchFromScratch"]
    canvasData: str = Field(..., description="Base64 encoded canvas data for drawings",
                            example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")
    alt: Optional[str] = Field(None, description="Alternative text for new or modified images",
                               example="Hand-drawn sketch of a castle")


class SketchOnImageOperation(BaseModel):
    type: Literal["sketchOnImage"]
    imageId: str = Field(..., description="Id of the existing image", example="img_891415125124_1")
    canvasData: str = Field(..., description="Base64 encoded canvas data for drawings",
                            example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")
    alt: Optional[str] = Field(None, description="Alternative text for new or modified images",
                               example="Hand-drawn sketch of a castle")


# Union type for all image operations
ImageOperation = Union[NoChangeOperation, SketchFromScratchOperation, SketchOnImageOperation]


class StoryState(str, Enum):
    pending = "pending"
    completed = "completed"

# Request Models
class CreateUserRequest(BaseModel):
    userName: str
    name: str


class DeleteUserRequest(BaseModel):
    userId: str


class CreateNewStoryRequest(BaseModel):
    userId: str
    storyName: str


class SetStoryNameRequest(BaseModel):
    userId: str
    storyId: str
    storyName: str


class DeleteStoryRequest(BaseModel):
    userId: str
    storyId: str


class UpdateImagesByTextRequest(BaseModel):
    userId: str
    storyId: str
    updatedText: str


class UpdateTextByImagesRequest(BaseModel):
    userId: str
    storyId: str
    imageOperations: List[ImageOperation] = Field(...,
                                                  description="List of image operations to perform")


class UploadImageRequest(BaseModel):
    userId: str
    storyId: str
    imageFile: str


# Response Models
class UserResponse(BaseModel):
    userId: str
    name: str
    userName: str
    accountCreated: str
    model_config = ConfigDict(from_attributes=True)


class StoryBasicInfoResponse(BaseModel):
    storyId: str
    coverImage: str
    storyName: str
    lastEdited: str


class ImageResponse(BaseModel):
    imageId: str
    url: str
    alt: str


class StoryDetailsResponse(BaseModel):
    storyId: str
    storyName: str
    storyText: str
    state: StoryState
    storyImages: List[ImageResponse]


class UserStoriesResponse(BaseModel):
    stories: List[StoryBasicInfoResponse]
