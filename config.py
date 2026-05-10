import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:bhavesh13@localhost:5433/event_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'chansy15'
    JWT_SECRET_KEY = 'chansy15'