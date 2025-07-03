from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db import engine


def update_user_aggregates(user_id: int, conn=None):
    # If no connection passed, open a new one
    if conn is None:
        with engine.begin() as conn:
            _update_aggregates(user_id, conn)
    else:
        _update_aggregates(user_id, conn)

def _update_aggregates(user_id: int, conn):
    try:
        income_result = conn.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = :user_id AND type = 'income'"),
            {"user_id": user_id}
        ).scalar()

        expense_result = conn.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = :user_id AND type = 'expense'"),
            {"user_id": user_id}
        ).scalar()

        balance = income_result - expense_result
        savings = balance

        conn.execute(
            text("""
                UPDATE users
                SET total_income = :income,
                    total_expense = :expense,
                    balance = :balance,
                    savings = :savings
                WHERE id = :user_id
            """),
            {
                "income": income_result,
                "expense": expense_result,
                "balance": balance,
                "savings": savings,
                "user_id": user_id
            }
        )
    except SQLAlchemyError as e:
        print(f"❌ Error updating user aggregates: {e}")
        raise
