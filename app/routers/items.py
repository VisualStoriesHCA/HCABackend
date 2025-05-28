# app/routers/items.py
from typing import Optional, List, Dict

from fastapi import APIRouter, status, HTTPException

from ..models.session import get_user_session, create_user_session, generate_user_id

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

router = APIRouter()
@router.post("/createNewUser", status_code=status.HTTP_201_CREATED)
async def create_new_user(
        userName: str,
        name: str,
):
    user_id = generate_user_id(userName)
    if get_user_session(user_id):
        raise HTTPException(
            status_code=400,
            detail=f"User '{userName}' already exists"
        )

    user = create_user_session(name=name,
                               user_name=userName,
                               user_id=user_id)
    return user.to_dict()

@router.get("/getUserInformation")
async def get_user_information(
        userId: str
):
    user = get_user_session(userId)
    return user.to_dict()


@router.get("/getUserStories")
async def get_user_stories(
        userId: str,
        maxEntries: Optional[int] = 50,
):
    user = get_user_session(userId)
    return {
        "stories": [story.to_story_basic_information() for story in user.get_stories(maxEntries)]
    }


@router.get("/getStoryById")
async def get_story_by_id(
        userId: str,
        storyId: str
):
    user = get_user_session(userId)
    return user.get_story(storyId).to_story_details_response()


@router.post("/updateImagesByText")
async def update_images_by_text(
        userId: str,
        storyId: str,
        updatedText: str,
):
    user = get_user_session(userId)
    story = user.get_story(storyId)
    story.set_text(updatedText)
    story.update_images_by_text()
    return story.to_story_details_response()


@router.post("/updateTextByImages")
async def update_text_by_images(
        userId: str,
        storyId: str,
        imageOperations: List[Dict],
):
    user = get_user_session(userId)
    story = user.get_story(storyId)
    story.update_from_image_operations(imageOperations)
    return story.to_story_details_response()
