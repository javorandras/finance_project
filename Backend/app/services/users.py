from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserResponse, UserUpdateRequest

def get_user_profile(user_id: int, db: Session) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


def update_user_profile(update_data: UserUpdateRequest, user_id: int, db: Session) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)

