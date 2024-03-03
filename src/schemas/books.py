from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook", "ReturnedBookWithSeller"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Класс книг с ID продавца
class BookWithSeller(BaseBook):
    seller_id: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BookWithSeller):
    year: int = 2024  # Пример присваивания дефолтного значения
    count_pages: int = Field(
        alias="pages",
        default=300,
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBookWithSeller(BookWithSeller):
    id: int
    count_pages: int


# Класс, возвращающий книги без продавца
class ReturnedBook(BaseBook):
    id: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBookWithSeller]
