# app/routers/items.py
from typing import Optional, List, Dict

from fastapi import APIRouter

from ..models.session import get_user_session

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

router = APIRouter()


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
