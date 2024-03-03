from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations.database import get_async_session

from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks
from src.models.seller import Seller
from src.models.books import Book

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД. Возвращает созданного продавца.
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller.id, Seller.first_name, Seller.last_name, Seller.email)
    res = await session.execute(query)
    sellers = [{"id": row.id, "first_name": row.first_name, "last_name": row.last_name, "email": row.email} for row in res]
    return {"sellers": sellers}


# Ручка для получения продавца по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    query = select(Book.id, Book.title, Book.author, Book.year, Book.count_pages).where(Book.seller_id == seller_id)
    res = await session.execute(query)
    books = [{"id": row.id, "title": row.title, "author": row.author,
              "year": row.year, "count_pages": row.count_pages} for row in res]
    return {"id": seller.id, "first_name": seller.first_name, "last_name": seller.last_name,
            "email": seller.email, "books": books}


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        query = select(Book).where(Book.seller_id == seller_id)
        res = await session.execute(query)
        books = res.scalars().all()
        for book in books:
            await session.delete(book)
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
