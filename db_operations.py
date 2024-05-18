from fastapi import HTTPException
from passlib.context import CryptContext
from driver.mongo import get_db_mongo
from driver.mysql import get_db_mysql_instance
import mysql.connector
from datetime import datetime, timedelta
from auth_utils import (
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def register_user(username: str, password: str):
    db, cursor = get_db_mysql_instance()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    hashed_password = get_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password),
        )
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"User registration failed: {err}")
    finally:
        cursor.close()
        db.close()


def get_user_by_username(username: str):
    db, cursor = get_db_mysql_instance()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user


def create_user_tokens(user):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}, expires_delta=refresh_token_expires
    )

    db, cursor = get_db_mysql_instance()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor.execute(
            "INSERT INTO access_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user["id"], access_token, datetime.utcnow() + access_token_expires),
        )
        cursor.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user["id"], refresh_token, datetime.utcnow() + refresh_token_expires),
        )
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Token creation failed: {err}")
    finally:
        cursor.close()
        db.close()

    return access_token, refresh_token


def delete_refresh_token(refresh_token: str):
    db, cursor = get_db_mysql_instance()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (refresh_token,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Token deletion failed: {err}")
    finally:
        cursor.close()
        db.close()


def insert_operacao_mongo(operacao):
    db = get_db_mongo()
    operacoes_collection = db["operacoes"]
    operacao_doc = {
        "user_id": operacao.user_id,
        "type": operacao.type,
        "amount": operacao.amount,
        "date": operacao.date,
        "description": operacao.description,
        "source": operacao.source,
    }

    result = operacoes_collection.insert_one(operacao_doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Erro ao criar a operação")
