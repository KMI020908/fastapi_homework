from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str

    @field_validator("first_name", "last_name")
    @staticmethod
    def validate_name(name: str):
        if len(name) == 0:
            raise PydanticCustomError("Validation error", "Name is empty!")
        return name

    @field_validator("email")
    @staticmethod
    def validate_login(email: str):
        try:
            validate_email(email)
        except EmailNotValidError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return email

    @field_validator("password")
    @staticmethod
    def validate_password(password: str):
        if len(password) == 0:
            raise PydanticCustomError("Validation error", "Password is empty!")
        return password


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
