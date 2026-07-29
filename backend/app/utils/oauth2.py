from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.config import settings
from app import models, schemas


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        print("hey")
        print("PAYLOAD:", payload)

        user_id = payload.get("user_id")
        role = payload.get("role")

        if user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(
            id=user_id,
            role=role
        )

        return token_data

    except JWTError:
        raise credentials_exception



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(
        token,
        credentials_exception
    )

    user = db.query(models.User).filter(
        models.User.id == token_data.id
    ).first()

    if user is None:
        raise credentials_exception

    return user