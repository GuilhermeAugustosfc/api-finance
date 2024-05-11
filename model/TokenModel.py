import secrets
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.MySQLDatabase import Base


def generate_client_secret(length: int = 32) -> str:
    # Gera uma sequência de bytes aleatórios
    secret_bytes = secrets.token_bytes(length)

    # Codifica a sequência de bytes como uma string hexadecimal
    client_secret = secret_bytes.hex()

    return client_secret


# Models
class OAuth2Client(Base):
    __tablename__ = "oauth2_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), unique=True, index=True)
    client_secret = Column(String(255))
    redirect_uri = Column(String(255))


class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    client_id = Column(Integer, ForeignKey("oauth2_clients.id"))
    client = relationship("OAuth2Client")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    expire_at = Column(DateTime)
    access_token_id = Column(Integer, ForeignKey("access_tokens.id"))
    access_token = relationship("AccessToken")
