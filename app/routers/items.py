# app/routers/items.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..models.db import SessionLocal
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

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@router.post("/createNewUser", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_new_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    user_id = generate_user_id(request.userName)
    existing_user = db.query(User).filter(User.userId == user_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"User '{request.userName}' already exists")

    new_user = User(userId=user_id, name=request.name, userName=request.userName)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.from_orm(new_user)


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: DeleteUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == request.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router.get("/getUserInformation", response_model=UserResponse)
async def get_user_information(userId: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.get("/getUserInformationByUserName", response_model=UserResponse)
async def get_user_information_by_user_name(userName: str = Query(...),
                                            db: Session = Depends(get_db)):
    user_id = generate_user_id(userName)
    user = db.query(User).filter(User.userId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.post("/createNewStory", response_model=StoryBasicInfoResponse)
async def create_new_story(request: CreateNewStoryRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == request.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = user.create_story(story_name=request.storyName)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story.to_story_basic_information()


@router.post("/setStoryName", response_model=StoryBasicInfoResponse)
async def set_story_name(request: SetStoryNameRequest, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == request.storyId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.name = request.storyName
    db.commit()
    db.refresh(story)
    return story.to_story_basic_information()


@router.delete("/deleteStory", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(request: DeleteStoryRequest, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == request.storyId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(story)
    db.commit()


@router.get("/getUserStories", response_model=UserStoriesResponse, operation_id="getUserStories")
async def get_user_stories(userId: str = Query(...),
                           maxEntries: int = Query(50),
                           db: Session = Depends(get_db)
                           ):
    stories = db.query(Story).filter(Story.userId == userId).limit(maxEntries).all()
    return {"stories": reversed([story.to_story_basic_information() for story in stories])}


@router.get("/getStoryById", response_model=StoryDetailsResponse)
async def get_story_by_id(userId: str, storyId: str, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == storyId, Story.userId == userId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story.to_story_details_response()


@router.post("/updateImagesByText", response_model=StoryDetailsResponse)
async def update_images_by_text(request: UpdateImagesByTextRequest, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == request.storyId, Story.userId == request.userId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_images_by_text(request.updatedText)
    db.commit()
    return story.to_story_details_response()


@router.post("/updateTextByImages", response_model=StoryDetailsResponse)
async def update_text_by_images(request: UpdateTextByImagesRequest, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == request.storyId, Story.userId == request.userId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.update_from_image_operations([op.model_dump() for op in request.imageOperations])
    db.commit()
    return story.to_story_details_response()


@router.post("/uploadImage", response_model=StoryDetailsResponse)
async def upload_image(request: UploadImageRequest, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.storyId == request.storyId, Story.userId == request.userId).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.upload_image(request.imageFile)
    db.commit()
    return story.to_story_details_response()
