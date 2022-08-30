from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]

class Configuration:
    # za dev
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost/authentication"
    # za deploy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/authentication"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
