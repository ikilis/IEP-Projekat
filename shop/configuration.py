from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]

class Configuration:
    # za dev
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/shopDB"
    # za deploy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shopDB"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # za dev
    # REDIS_HOST = "localhost"
    # za dep
    REDIS_HOST = os.environ["REDIS_PORT"]
    REDIS_PRODUCT_LIST = 'products'
