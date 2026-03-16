from sqlmodel import create_engine, Session, SQLModel


class DatabaseConfig:
    def __init__(self, db_path: str = "sqlite:///Database/food_service.db"):
        self.engine = create_engine(db_path, echo=True)

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        with Session(self.engine) as session:
            yield session


db = DatabaseConfig()
