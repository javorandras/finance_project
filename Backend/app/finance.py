from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models import Transaction, User
from fastapi import HTTPException, status

def update_user_aggregates(user_id: int, db: Session):
    try:
        income = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id, Transaction.type == "income"
        ).scalar() or 0

        expense = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id, Transaction.type == "expense"
        ).scalar() or 0

        balance = income - expense
        savings = balance

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.total_income = income
        user.total_expense = expense
        user.balance = balance
        user.savings = savings
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating user aggregates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update aggregates")