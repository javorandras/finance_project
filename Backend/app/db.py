from sqlalchemy import create_engine, inspect, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

def test_db_connection():
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ MySQL connection successful: {result.scalar()}")

            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables found: {tables}")

            for table in tables:
                print(f"\n🔎 Contents of table '{table}':")
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                column_names = result.keys()

                if not rows:
                    print("  (No rows found)")
                else:
                    print("  | " + " | ".join(column_names) + " |")
                    for row in rows:
                        print("  | " + " | ".join(str(value) for value in row) + " |")

    except Exception as e:
        print(f"❌ Error: {e}")
