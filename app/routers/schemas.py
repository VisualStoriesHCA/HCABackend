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
    error = "error"


# Achievement Enums
class AchievementType(str, Enum):
    progress = "progress"
    milestone = "milestone"
    binary = "binary"


class AchievementState(str, Enum):
    locked = "locked"
    in_progress = "in_progress"
    completed = "completed"


# Achievement Models
class AchievementReward(BaseModel):
    points: Optional[int] = None
    badge: Optional[str] = None
    unlocks: Optional[List[str]] = None


class UserAchievement(BaseModel):
    achievementId: int
    title: str
    description: str
    category: str
    type: AchievementType
    imageUrl: str
    state: AchievementState
    currentValue: int
    targetValue: int
    unit: str
    completedAt: Optional[str] = None
    reward: Optional[AchievementReward] = None
    unlockCondition: Optional[str] = None


class UserAchievementsResponse(BaseModel):
    achievements: List[UserAchievement]


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


class GenerateAudioRequest(BaseModel):
    userId: str
    storyId: str
    text: str


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

class StorySettings(BaseModel):
    imageModelId: int
    drawingStyleId: int
    colorBlindOptionId: int
    regenerateImage: bool

class StoryDetailsResponse(BaseModel):
    storyId: str
    storyName: str
    storyText: str
    state: StoryState
    storyImages: List[ImageResponse]
    audioUrl: Optional[str] = None
    settings: StorySettings  


class UserStoriesResponse(BaseModel):
    stories: List[StoryBasicInfoResponse]

class ImageModelResponse(BaseModel):
    imageModelId: int
    name: str
    description: str
    disabled: bool


class DrawingStyleResponse(BaseModel):
    drawingStyleId: int
    name: str
    description: str
    exampleImageUrl: Optional[str] = None
    disabled: bool


class ColorBlindOptionResponse(BaseModel):
    colorBlindOptionId: int
    name: str
    description: str


class AvailableSettingsResponse(BaseModel):
    availableImageModels: List[ImageModelResponse]
    availableDrawingStyles: List[DrawingStyleResponse]
    colorBlindOptions: List[ColorBlindOptionResponse]



# Request Models
class SetStoryOptionsRequest(BaseModel):
    userId: str
    storyId: str
    imageModelId: Optional[int] = None
    drawingStyleId: Optional[int] = None
    colorBlindOptionId: Optional[int] = None
    regenerateImage: Optional[bool] = None
