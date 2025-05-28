# app/routers/items.py
from typing import Optional, List, Dict

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

from ..models.session import get_user_session, create_user_session, generate_user_id, delete_user_session

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

router = APIRouter()


class CreateUserRequest(BaseModel):
    userName: str
    name: str


class DeleteUserRequest(BaseModel):
    userId: str


class GetUserInformationRequest(BaseModel):
    userId: str


class GetUserInformationByUserNameRequest(BaseModel):
    userName: str


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


class GetUserStoriesRequest(BaseModel):
    userId: str
    maxEntries: Optional[int] = 50


class GetStoryByIdRequest(BaseModel):
    userId: str
    storyId: str


class UpdateImagesByTextRequest(BaseModel):
    userId: str
    storyId: str
    updatedText: str


class UpdateTextByImagesRequest(BaseModel):
    userId: str
    storyId: str
    imageOperations: List[Dict]


class UploadImageRequest(BaseModel):
    userId: str
    storyId: str
    imageFile: str


@router.post("/createNewUser", status_code=status.HTTP_201_CREATED)
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


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        request: DeleteUserRequest
):
    success = delete_user_session(request.userId)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/getUserInformation")
async def get_user_information(
        request: GetUserInformationRequest
):
    user = get_user_session(request.userId)
    return user.to_dict()


@router.get("/getUserInformationByUserName")
async def get_user_information_by_user_name(
        request: GetUserInformationByUserNameRequest
):
    user_id = generate_user_id(request.userName)
    user = get_user_session(user_id)
    return user.to_dict()


@router.post("/createNewStory", status_code=status.HTTP_201_CREATED)
async def create_new_story(
        request: CreateNewStoryRequest,
):
    user = get_user_session(request.userId)
    story_id = user.create_story(story_name=request.storyName)
    return user.get_story(story_id).to_story_basic_information()


@router.post("/setStoryName", status_code=status.HTTP_201_CREATED)
async def set_story_name(
        request: SetStoryNameRequest
):
    user = get_user_session(request.userId)
    story = user.get_story(story_id=request.storyId)
    story.set_story_name(request.storyName)
    return story.to_story_basic_information()


@router.delete("/deleteStory", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
        request: DeleteStoryRequest
):
    user = get_user_session(request.userId)
    success = user.delete_story(request.storyId)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")


@router.get("/getUserStories")
async def get_user_stories(
        request: GetUserStoriesRequest
):
    user = get_user_session(request.userId)
    return {
        "stories": [story.to_story_basic_information() for story in user.get_stories(request.maxEntries)]
    }


@router.get("/getStoryById")
async def get_story_by_id(
        request: GetStoryByIdRequest
):
    user = get_user_session(request.userId)
    return user.get_story(request.storyId).to_story_details_response()


@router.post("/updateImagesByText")
async def update_images_by_text(
        request: UpdateImagesByTextRequest
):
    user = get_user_session(request.userId)
    story = user.get_story(request.storyId)
    story.set_text(request.updatedText)
    story.update_images_by_text()
    return story.to_story_details_response()


@router.post("/updateTextByImages")
async def update_text_by_images(
        request: UpdateTextByImagesRequest
):
    user = get_user_session(request.userId)
    story = user.get_story(request.storyId)
    story.update_from_image_operations(request.imageOperations)
    return story.to_story_details_response()


@router.post("/uploadImage")
async def upload_image(
        request: UploadImageRequest
):
    user = get_user_session(request.userId)
    story = user.get_story(request.storyId)
    story.upload_image(request.imageFile)
    return story.to_story_details_response()
