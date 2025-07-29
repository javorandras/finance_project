from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User, RefreshToken, Transaction
from app.schemas import AdminUserResponse, AdminUpdateRequest
from datetime import datetime, timezone

def get_logged_in_users(db: Session) -> list[AdminUserResponse]:
    results = (
        db.query(User)
        .join(RefreshToken)
        .filter(RefreshToken.expires_at > datetime.now(timezone.utc))
        .group_by(User.id)
        .order_by(RefreshToken.created_at.desc())
        .all()
    )
    return [AdminUserResponse.model_validate(user) for user in results]

def set_user_admin(user_id: int, update: AdminUpdateRequest, current_user: int, db: Session) -> dict:
    if user_id == current_user and not update.is_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove admin rights from yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_admin = update.is_admin
    db.commit()
    return {"message": f"User {user_id} admin status set to {update.is_admin}"}

def delete_user(user_id: int, current_user: int, db: Session) -> dict:
    if user_id == current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own user")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}

def logout_all_users(db: Session) -> dict:
    db.query(RefreshToken).delete()
    db.commit()
    return {"message": "All users have been logged out (refresh_tokens table truncated)"}