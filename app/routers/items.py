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
        userID: str
):
    user = get_user_session(userID)
    return user.to_dict()


@router.get("/getUserStories")
async def get_user_stories(
        userID: str,
        maxEntries: Optional[int] = 50,
):
    user = get_user_session(userID)
    return {
        "stories": [story.to_story_basic_information() for story in user.get_stories(maxEntries)]
    }


@router.get("/getStoryByID")
async def get_story_by_id(
        userID: str,
        storyID: str
):
    user = get_user_session(userID)
    return user.get_story(storyID).to_story_details_response()


@router.post("/updateImagesByText")
async def update_images_by_text(
        userID: str,
        storyID: str,
        updatedText: str,
):
    user = get_user_session(userID)
    story = user.get_story(storyID)
    story.set_text(updatedText)
    story.update_images_by_text()
    return story.to_story_details_response()


@router.post("/updateTextByImages")
async def update_text_by_images(
        userID: str,
        storyID: str,
        imageOperations: List[Dict],
):
    user = get_user_session(userID)
    story = user.get_story(storyID)
    story.update_from_image_operations(imageOperations)
    return story.to_story_details_response()
