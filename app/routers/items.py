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
    UpdateTextByImagesRequest, UploadImageRequest, StoryState,
    UserAchievementsResponse, UserAchievement, AchievementType,
    AchievementState, AchievementReward, GenerateAudioRequest
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


@router.post("/createNewUser", status_code=status.HTTP_201_CREATED, response_model=UserResponse, operation_id="createNewUser")
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


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteUser")
async def delete_user(request: DeleteUserRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(userId=request.userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()


@router.get("/getUserInformation", response_model=UserResponse, operation_id="getUserInformation")
async def get_user_information(userId: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(userId=userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.get("/getUserInformationByUserName", response_model=UserResponse, operation_id="getUserInformationByUserName")
async def get_user_information_by_user_name(userName: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    user_id = generate_user_id(userName)
    result = await db.execute(select(User).filter_by(userId=user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.post("/createNewStory", response_model=StoryBasicInfoResponse, operation_id="createNewStory")
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


@router.post("/setStoryName", response_model=StoryBasicInfoResponse, operation_id="setStoryName")
async def set_story_name(request: SetStoryNameRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.name = request.storyName
    await db.commit()
    await db.refresh(story)
    return story.to_story_basic_information()


@router.delete("/deleteStory", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteStory")
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


@router.get("/getStoryById", response_model=StoryDetailsResponse, operation_id="getStoryById")
async def get_story_by_id(userId: str, storyId: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=storyId, userId=userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story.to_story_details_response()


@router.get("/getUserAchievements", response_model=UserAchievementsResponse, operation_id="getUserAchievements")
async def get_user_achievements(userId: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    """
    Get all achievements and user progress for gamification features.

    This is a placeholder implementation that returns static example data.
    TODO: Implement actual database queries when Achievement and UserAchievement tables are created.
    """

    # Verify user exists
    result = await db.execute(select(User).filter_by(userId=userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Static example data - replace with actual database queries later
    static_achievements = [
        UserAchievement(
            achievementId=1,
            title="Storyteller",
            description="Write your first 10 stories",
            category="story_creation",
            type=AchievementType.progress,
            imageUrl="https://example.com/badges/storyteller.png",
            state=AchievementState.in_progress,
            currentValue=7,
            targetValue=10,
            unit="stories",
            completedAt=None,
            reward=AchievementReward(
                points=100,
                badge="Bronze Storyteller"
            ),
            unlockCondition=None
        ),
        UserAchievement(
            achievementId=2,
            title="Epic Novelist",
            description="Write a story with at least 1000 words",
            category="creativity",
            type=AchievementType.milestone,
            imageUrl="https://example.com/badges/novelist.png",
            state=AchievementState.completed,
            currentValue=1247,
            targetValue=1000,
            unit="words",
            completedAt="2025-06-20T14:30:00Z",
            reward=AchievementReward(
                points=250,
                badge="Epic Novelist",
                unlocks=["advanced_writing_tools"]
            ),
            unlockCondition=None
        ),
        UserAchievement(
            achievementId=3,
            title="Master Editor",
            description="Make 25 edits to your stories",
            category="creativity",
            type=AchievementType.progress,
            imageUrl="https://example.com/badges/editor.png",
            state=AchievementState.in_progress,
            currentValue=12,
            targetValue=25,
            unit="edits",
            completedAt=None,
            reward=AchievementReward(
                points=150,
                badge="Master Editor"
            ),
            unlockCondition=None
        ),
        UserAchievement(
            achievementId=4,
            title="Consistent Creator",
            description="Write stories for 7 consecutive days",
            category="consistency",
            type=AchievementType.progress,
            imageUrl="https://example.com/badges/consistent.png",
            state=AchievementState.locked,
            currentValue=0,
            targetValue=7,
            unit="days",
            completedAt=None,
            reward=AchievementReward(
                points=300,
                badge="Consistent Creator"
            ),
            unlockCondition="Complete 'Storyteller' achievement"
        )
    ]

    return UserAchievementsResponse(achievements=static_achievements)


@router.post("/updateImagesByText", response_model=StoryDetailsResponse, operation_id="updateImagesByText")
async def update_images_by_text(request: UpdateImagesByTextRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    logger.debug("Calling update_images_by_text")
    story.update_state(StoryState.pending)
    await db.commit()
    await db.refresh(story)
    await story.update_images_by_text(request.updatedText)
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()


@router.post("/updateTextByImages", response_model=StoryDetailsResponse, operation_id="updateTextByImages")
async def update_text_by_images(request: UpdateTextByImagesRequest, db: AsyncSession = Depends(get_async_db)):
    logger.debug(f"Calling '/updateTextByImages'")
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_state(StoryState.pending)
    await db.commit()
    await db.refresh(story)
    await story.update_from_image_operations([op.model_dump() for op in request.imageOperations])
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()


@router.post("/uploadImage", response_model=StoryDetailsResponse, operation_id="uploadImage")
async def upload_image(request: UploadImageRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_state(StoryState.pending)
    await db.commit()
    await db.refresh(story)
    
    try:
        await story.upload_image(request.imageFile)
    except ValueError as e:
        # Rollback the state change if image upload fails
        story.update_state(StoryState.completed)
        await db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()


@router.post("/generateAudio", response_model=StoryDetailsResponse, operation_id="generateAudio")
async def generate_audio(request: GenerateAudioRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_state(StoryState.pending)
    await db.commit()
    await db.refresh(story)
    await story.generate_audio(request.text)
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()
