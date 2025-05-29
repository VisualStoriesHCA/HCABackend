# app/routers/items.py
from typing import Optional, List, Dict, Union, Literal

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field

from ..models.session import get_user_session, create_user_session, generate_user_id, delete_user_session

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

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
    storyImages: List[ImageResponse]


class UserStoriesResponse(BaseModel):
    stories: List[StoryBasicInfoResponse]


# Endpoints
@router.post("/createNewUser", status_code=status.HTTP_201_CREATED, response_model=UserResponse, operation_id="createUser")
async def create_new_user(
        request: CreateUserRequest
):
    user_id = generate_user_id(request.userName)
    if get_user_session(user_id):
        raise HTTPException(
            status_code=400,
            detail=f"User '{request.userName}' already exists"
        )

    user = create_user_session(name=request.name,
                               user_name=request.userName,
                               user_id=user_id)
    return user.to_dict()


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteUser")
async def delete_user(
        request: DeleteUserRequest
):
    success = delete_user_session(request.userId)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/getUserInformation", response_model=UserResponse, operation_id="getUserInfo")
async def get_user_information(
        userId: str
):
    user = get_user_session(userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@router.get("/getUserInformationByUserName", response_model=UserResponse, operation_id="getUserInfoByUsername")
async def get_user_information_by_user_name(
        userName: str
):
    user_id = generate_user_id(userName)
    user = get_user_session(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@router.post("/createNewStory", status_code=status.HTTP_201_CREATED, response_model=StoryBasicInfoResponse, operation_id="createStory")
async def create_new_story(
        request: CreateNewStoryRequest,
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story_id = user.create_story(story_name=request.storyName)
    return user.get_story(story_id).to_story_basic_information()


@router.post("/setStoryName", status_code=status.HTTP_201_CREATED, response_model=StoryBasicInfoResponse, operation_id="updateStoryName")
async def set_story_name(
        request: SetStoryNameRequest
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.get_story(story_id=request.storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.set_story_name(request.storyName)
    return story.to_story_basic_information()


@router.delete("/deleteStory", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteStory")
async def delete_story(
        request: DeleteStoryRequest
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = user.delete_story(request.storyId)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")


@router.get("/getUserStories", response_model=UserStoriesResponse, operation_id="getUserStories")
async def get_user_stories(
        userId: str,
        maxEntries: Optional[int] = 50
):
    user = get_user_session(userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "stories": [story.to_story_basic_information() for story in user.get_stories(maxEntries)]
    }


@router.get("/getStoryById", response_model=StoryDetailsResponse, operation_id="getStory")
async def get_story_by_id(
        userId: str,
        storyId: str
):
    user = get_user_session(userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.get_story(storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story.to_story_details_response()


@router.post("/updateImagesByText", response_model=StoryDetailsResponse, operation_id="updateImagesByText")
async def update_images_by_text(
        request: UpdateImagesByTextRequest
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.get_story(request.storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.set_text(request.updatedText)
    story.update_images_by_text()
    return story.to_story_details_response()


@router.post("/updateTextByImages", response_model=StoryDetailsResponse, operation_id="updateTextByImages")
async def update_text_by_images(
        request: UpdateTextByImagesRequest
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.get_story(request.storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    # Convert Pydantic models to dicts for backward compatibility
    image_operations_dicts = [op.model_dump() for op in request.imageOperations]
    story.update_from_image_operations(image_operations_dicts)
    return story.to_story_details_response()


@router.post("/uploadImage", response_model=StoryDetailsResponse, operation_id="uploadImage")
async def upload_image(
        request: UploadImageRequest
):
    user = get_user_session(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.get_story(request.storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.upload_image(request.imageFile)
    return story.to_story_details_response()