# from typing import Annotated
# from passlib.context import CryptContext
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from jose import JWTError, jwt
# from datetime import datetime, timedelta, timezone
# from fastapi import APIRouter, Depends, Response, status
# from src.configurations.settings import settings


# token_router = APIRouter(tags=["token"], prefix="/token")

# SECRET_KEY = settings.secret_key
# ALGORITHM = settings.algorithm
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class TokenData(BaseModel):
#     username: str | None = None


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# @token_router.post("/")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ) -> Token:
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")