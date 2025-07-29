from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Transaction
from app.schemas import TransactionCreateRequest, TransactionUpdateRequest, TransactionResponse
from app.finance import update_user_aggregates


class TransactionService:
    @staticmethod
    def verify_transaction_ownership(db: Session, transaction_id: int, user_id: int) -> int:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        if transaction.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not authorized to access this transaction")
        return transaction.user_id


def get_transactions(user_id: int, skip: int, limit: int, db: Session) -> list[TransactionResponse]:
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [TransactionResponse.from_orm(t) for t in transactions]


def create_transaction(transaction: TransactionCreateRequest, user_id: int, db: Session) -> dict:
    new_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        type=transaction.type,
        description=transaction.description or "",
        date=datetime.now(timezone.utc)
    )
    db.add(new_transaction)
    db.commit()
    update_user_aggregates(user_id, db)
    return {"message": "Transaction added and aggregates updated"}


def update_transaction(transaction: TransactionUpdateRequest, transaction_id: int, user_id: int, db: Session) -> dict:
    TransactionService.verify_transaction_ownership(db, transaction_id, user_id)
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    for field, value in transaction.dict(exclude_unset=True).items():
        setattr(db_transaction, field, value)
    db.commit()
    update_user_aggregates(user_id, db)
    return {
        "message": f"Transaction with ID {transaction_id} updated successfully and aggregates updated",
        "transaction_id": transaction_id
    }


def delete_transaction(transaction_id: int, user_id: int, db: Session) -> dict:
    user_id = TransactionService.verify_transaction_ownership(db, transaction_id, user_id)
    db.query(Transaction).filter(Transaction.id == transaction_id).delete()
    db.commit()
    update_user_aggregates(user_id, db)
    return {
        "message": f"Transaction with ID {transaction_id} deleted successfully and aggregates updated",
        "transaction_id": transaction_id
    }