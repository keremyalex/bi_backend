from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

def get_engine(db_url: str):
    return create_engine(db_url)

def probar_conexion(db_url: str):
    try:
        engine = get_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        print("❌ ERROR al conectar:", e)
        raise e  # para que el handler de FastAPI lo muestre
        # return False

def get_tables(db_url: str):
    engine = get_engine(db_url)
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_columns(db_url: str, table_name: str):
    engine = get_engine(db_url)
    inspector = inspect(engine)
    return inspector.get_columns(table_name)
