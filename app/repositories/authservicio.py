from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.usuario import Usuario as User
from app.repositories.user_repository import get_user_by_email
from app.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data):

    existing_user = get_user_by_email(db, data.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(db: Session, data):

    user = get_user_by_email(db, data.email)

    if not user or not verify_password(
        data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
