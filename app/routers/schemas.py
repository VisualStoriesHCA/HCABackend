from typing import Optional, List, Union, Literal

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


# Image Operation Models
class NoChangeOperation(BaseModel):
    type: Literal["nochange"]
    imageId: str = Field(..., description="Id of the existing image", example="img_891415125124_1")
    model_config = ConfigDict(from_attributes=True)


class SketchFromScratchOperation(BaseModel):
    type: Literal["sketchFromScratch"]
    canvasData: str = Field(..., description="Base64 encoded canvas data for drawings",
                            example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")
    alt: Optional[str] = Field(None, description="Alternative text for new or modified images",
                               example="Hand-drawn sketch of a castle")
    model_config = ConfigDict(from_attributes=True)


class SketchOnImageOperation(BaseModel):
    type: Literal["sketchOnImage"]
    imageId: str = Field(..., description="Id of the existing image", example="img_891415125124_1")
    canvasData: str = Field(..., description="Base64 encoded canvas data for drawings",
                            example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")
    alt: Optional[str] = Field(None, description="Alternative text for new or modified images",
                               example="Hand-drawn sketch of a castle")


# Union type for all image operations
ImageOperation = Union[NoChangeOperation, SketchFromScratchOperation, SketchOnImageOperation]


# Request Models
class CreateUserRequest(BaseModel):
    userName: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class DeleteUserRequest(BaseModel):
    userId: str
    model_config = ConfigDict(from_attributes=True)


class CreateNewStoryRequest(BaseModel):
    userId: str
    storyName: str
    model_config = ConfigDict(from_attributes=True)


class SetStoryNameRequest(BaseModel):
    userId: str
    storyId: str
    storyName: str
    model_config = ConfigDict(from_attributes=True)


class DeleteStoryRequest(BaseModel):
    userId: str
    storyId: str
    model_config = ConfigDict(from_attributes=True)


class UpdateImagesByTextRequest(BaseModel):
    userId: str
    storyId: str
    updatedText: str
    model_config = ConfigDict(from_attributes=True)


class UpdateTextByImagesRequest(BaseModel):
    userId: str
    storyId: str
    imageOperations: List[ImageOperation] = Field(...,
                                                  description="List of image operations to perform")
    model_config = ConfigDict(from_attributes=True)


class UploadImageRequest(BaseModel):
    userId: str
    storyId: str
    imageFile: str
    model_config = ConfigDict(from_attributes=True)


# Response Models
class UserResponse(BaseModel):
    userId: str = Field(alias="id")
    name: str = Field(alias="name")
    userName: str = Field(alias="user_name")
    accountCreated: str = Field(alias="account_created")
    model_config = ConfigDict(from_attributes=True)


class StoryBasicInfoResponse(BaseModel):
    storyId: str
    coverImage: str
    storyName: str
    lastEdited: str
    model_config = ConfigDict(from_attributes=True)


class ImageResponse(BaseModel):
    imageId: str
    url: str
    alt: str
    model_config = ConfigDict(from_attributes=True)


class StoryDetailsResponse(BaseModel):
    storyId: str
    storyName: str
    storyText: str
    storyImages: List[ImageResponse]
    model_config = ConfigDict(from_attributes=True)


class UserStoriesResponse(BaseModel):
    stories: List[StoryBasicInfoResponse]
    model_config = ConfigDict(from_attributes=True)
