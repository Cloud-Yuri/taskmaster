import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-muito-secreta-123456'
    
    # Railway fornece DATABASE_URL automaticamente
    # Se não estiver no Railway, usa SQLite local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///taskmaster.db'
    
    # Railway usa postgres://, mas SQLAlchemy precisa de postgresql://
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False