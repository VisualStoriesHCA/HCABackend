# app/routers/items.py

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.db import async_session
from ..models.structures import User, Story
from ..models.utils import generate_user_id
from ..routers.schemas import (
    CreateUserRequest, UserResponse,
    DeleteUserRequest, CreateNewStoryRequest,
    SetStoryNameRequest, DeleteStoryRequest,
    UserStoriesResponse, StoryBasicInfoResponse,
    StoryDetailsResponse, UpdateImagesByTextRequest,
    UpdateTextByImagesRequest, UploadImageRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


async def get_async_db():
    async with async_session() as session:
        yield session


@router.post("/createNewUser", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_new_user(request: CreateUserRequest, db: AsyncSession = Depends(get_async_db)):
    user_id = generate_user_id(request.userName)
    result = await db.execute(select(User).filter_by(userId=user_id))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"User '{request.userName}' already exists")

    new_user = User(userId=user_id, name=request.name, userName=request.userName)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse.from_orm(new_user)


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: DeleteUserRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(userId=request.userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()


@router.get("/getUserInformation", response_model=UserResponse)
async def get_user_information(userId: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(userId=userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.get("/getUserInformationByUserName", response_model=UserResponse)
async def get_user_information_by_user_name(userName: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    user_id = generate_user_id(userName)
    result = await db.execute(select(User).filter_by(userId=user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.post("/createNewStory", response_model=StoryBasicInfoResponse)
async def create_new_story(request: CreateNewStoryRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(userId=request.userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.create_story(story_name=request.storyName)
    db.add(story)
    await db.commit()
    await db.refresh(story)
    return story.to_story_basic_information()


@router.post("/setStoryName", response_model=StoryBasicInfoResponse)
async def set_story_name(request: SetStoryNameRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.name = request.storyName
    await db.commit()
    await db.refresh(story)
    return story.to_story_basic_information()


@router.delete("/deleteStory", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(request: DeleteStoryRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    await db.delete(story)
    await db.commit()


@router.get("/getUserStories", response_model=UserStoriesResponse, operation_id="getUserStories")
async def get_user_stories(userId: str = Query(...), maxEntries: int = Query(50),
                           db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(userId=userId).limit(maxEntries))
    stories = result.scalars().all()
    return {"stories": list(reversed([story.to_story_basic_information() for story in stories]))}


@router.get("/getStoryById", response_model=StoryDetailsResponse)
async def get_story_by_id(userId: str, storyId: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=storyId, userId=userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story.to_story_details_response()


@router.post("/updateImagesByText", response_model=StoryDetailsResponse)
async def update_images_by_text(request: UpdateImagesByTextRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    logger.debug("Calling update_images_by_text")
    await story.update_images_by_text(request.updatedText)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()


@router.post("/updateTextByImages", response_model=StoryDetailsResponse)
async def update_text_by_images(request: UpdateTextByImagesRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    await story.update_from_image_operations([op.model_dump() for op in request.imageOperations])
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()


@router.post("/uploadImage", response_model=StoryDetailsResponse)
async def upload_image(request: UploadImageRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.upload_image(request.imageFile)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()
