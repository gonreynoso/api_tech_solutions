import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "postgres")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_ACCESS_EXPIRES_HOURS = int(os.environ.get("JWT_ACCESS_EXPIRES_HOURS", "24"))
    JWT_REFRESH_EXPIRES_DAYS = int(os.environ.get("JWT_REFRESH_EXPIRES_DAYS", "30"))

    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    @staticmethod
    def db_dsn():
        return (
            f"host={Config.DB_HOST} port={Config.DB_PORT} "
            f"dbname={Config.DB_NAME} user={Config.DB_USER} "
            f"password={Config.DB_PASSWORD}"
        )
