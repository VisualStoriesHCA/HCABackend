# app/routers/items.py

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.db import async_session
from ..models.settings import ImageModel, DrawingStyle, ColorBlindOption
from ..models.structures import User, Story
from ..models.utils import generate_user_id
from ..routers.schemas import (
    CreateUserRequest, UserResponse,
    DeleteUserRequest, CreateNewStoryRequest,
    SetStoryNameRequest, DeleteStoryRequest,
    UserStoriesResponse, StoryBasicInfoResponse,
    StoryDetailsResponse, UpdateImagesByTextRequest,
    UpdateTextByImagesRequest, UploadImageRequest, StoryState,
    UserAchievementsResponse, GenerateAudioRequest,
    AvailableSettingsResponse, SetStoryOptionsRequest
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
    achievement = await user.update_achievement(achievementId="1", db=db)
    db.add(story)
    db.add(achievement)
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
    # Verify user exists
    result = await db.execute(select(User).filter_by(userId=userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user.get_achievements(db)


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
    try:
        await story.update_images_by_text(request.updatedText)
    except:
        story.update_state(StoryState.error)
        await db.commit()
        await db.refresh(story)
        raise HTTPException(status_code=400)
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    result = await db.execute(select(User).filter_by(userId=request.userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    achievement = await user.update_achievement(achievementId="2", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    achievement = await user.update_achievement(achievementId="3", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    achievement = await user.update_achievement(achievementId="4", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    return story.to_story_details_response()


@router.post("/updateTextByImages", response_model=StoryDetailsResponse, operation_id="updateTextByImages")
async def update_text_by_images(request: UpdateTextByImagesRequest, db: AsyncSession = Depends(get_async_db)):
    logger.debug(f"Calling '/updateTextByImages' with request {request}")
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_state(StoryState.pending)
    await db.commit()
    await db.refresh(story)
    logger.debug(f"Story - {story} - state has been updated to pending.")
    try:
        await story.update_from_image_operations([op.model_dump() for op in request.imageOperations])
    except:
        story.update_state(StoryState.error)
        await db.commit()
        await db.refresh(story)
        logger.debug(f"Story - {story} - state has been updated to error.")
        raise HTTPException(status_code=400)
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    logger.debug(f"Story - {story} - state has been updated to completed.")
    result = await db.execute(select(User).filter_by(userId=request.userId))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    achievement = await user.update_achievement(achievementId="2", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    achievement = await user.update_achievement(achievementId="3", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    achievement = await user.update_achievement(achievementId="4", db=db, story=story)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
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
        story.update_state(StoryState.error)
        await db.commit()
        await db.refresh(story)
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
    try:
        await story.generate_audio(request.text)
    except:
        story.update_state(StoryState.error)
        await db.commit()
        await db.refresh(story)
        raise HTTPException(status_code=400)
    story.update_state(StoryState.completed)
    await db.commit()
    await db.refresh(story)
    return story.to_story_details_response()

@router.get("/getAvailableSettings", response_model=AvailableSettingsResponse, operation_id="getAvailableSettings")
async def get_available_settings(db: AsyncSession = Depends(get_async_db)):
    """
    Get all available settings options for stories including image models, 
    drawing styles, and colorblind options.
    """
    # Get all image models
    image_models_result = await db.execute(select(ImageModel))
    image_models = image_models_result.scalars().all()
    
    # Get all drawing styles
    drawing_styles_result = await db.execute(select(DrawingStyle))
    drawing_styles = drawing_styles_result.scalars().all()
    
    # Get all colorblind options
    colorblind_options_result = await db.execute(select(ColorBlindOption))
    colorblind_options = colorblind_options_result.scalars().all()
    
    return AvailableSettingsResponse(
        availableImageModels=[model.to_dict() for model in image_models],
        availableDrawingStyles=[style.to_dict() for style in drawing_styles],
        colorBlindOptions=[option.to_dict() for option in colorblind_options]
    )


@router.post("/setStoryOptions", response_model=StoryDetailsResponse, operation_id="setStoryOptions")
async def set_story_options(request: SetStoryOptionsRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Update the settings (image model, drawing style, colorblind option) for a specific story.
    """
    # Get the story
    result = await db.execute(select(Story).filter_by(storyId=request.storyId, userId=request.userId))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Validate imageModelId if provided
    if request.imageModelId is not None:
        image_model_result = await db.execute(
            select(ImageModel).where(ImageModel.imageModelId == request.imageModelId)
        )
        image_model = image_model_result.scalar_one_or_none()
        if not image_model:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid imageModelId: {request.imageModelId}"
            )
        if image_model.disabled:
            raise HTTPException(
                status_code=400, 
                detail=f"Image model '{image_model.name}' is currently disabled"
            )
    
    # Validate drawingStyleId if provided
    if request.drawingStyleId is not None:
        drawing_style_result = await db.execute(
            select(DrawingStyle).where(DrawingStyle.drawingStyleId == request.drawingStyleId)
        )
        drawing_style = drawing_style_result.scalar_one_or_none()
        if not drawing_style:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid drawingStyleId: {request.drawingStyleId}"
            )
        if drawing_style.disabled:
            raise HTTPException(
                status_code=400, 
                detail=f"Drawing style '{drawing_style.name}' is currently disabled"
            )
    
    # Validate colorBlindOptionId if provided
    if request.colorBlindOptionId is not None:
        colorblind_option_result = await db.execute(
            select(ColorBlindOption).where(ColorBlindOption.colorBlindOptionId == request.colorBlindOptionId)
        )
        colorblind_option = colorblind_option_result.scalar_one_or_none()
        if not colorblind_option:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid colorBlindOptionId: {request.colorBlindOptionId}"
            )
    
    # Update the story settings
    story.update_settings(
        imageModelId=request.imageModelId,
        drawingStyleId=request.drawingStyleId,
        colorBlindOptionId=request.colorBlindOptionId,
        regenerateImage=request.regenerateImage
    )
    
    await db.commit()
    await db.refresh(story)
    
    return story.to_story_details_response()