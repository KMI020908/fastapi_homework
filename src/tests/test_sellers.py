import pytest
from fastapi import status
from sqlalchemy import select
from src.models import seller
from src.models import books


default_seller = {"first_name": "Ivan", "last_name": "Sidorov", "email": "example@mail.com", "password": "12345678"}
default_book = {"title": "Wrong Code", "author": "Robert Martin", "count_pages": 104, "year": 2007}


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = default_seller
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Sidorov",
        "email": "example@mail.com",
        "id": result_data['id']
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    user = seller.Seller(**default_seller)
    db_session.add(user)
    await db_session.flush()

    book = books.Book(**default_book, seller_id=user.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{user.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_seller_books = await db_session.execute(select(books.Book).where(books.Book.seller_id == user.id))
    book_res = all_seller_books.scalars().all()
    assert len(book_res) == 0

    all_sellers = await db_session.execute(select(seller.Seller))
    seller_res = all_sellers.scalars().all()
    assert len(seller_res) == 0


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    user = seller.Seller(first_name="Ivan", last_name="Ivanov", email="example@mail.com", password="123")
    user_2 = seller.Seller(first_name="Ksyusha", last_name="Razdorskaya", email="example@mail.com", password="321")
    user_3 = seller.Seller(first_name="Misha", last_name="Kochergin", email="example@mail.com", password="321")

    db_session.add_all([user, user_2, user_3])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Ivan", "last_name": "Ivanov", "email": "example@mail.com", "id": user.id},
            {"first_name": "Ksyusha", "last_name": "Razdorskaya", "email": "example@mail.com", "id": user_2.id},
            {"first_name": "Misha", "last_name": "Kochergin", "email": "example@mail.com", "id": user_3.id}
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    user = seller.Seller(**default_seller)
    db_session.add(user)
    await db_session.flush()

    n = 3
    books_lst = [books.Book(**default_book, seller_id=user.id) for _ in range(n)]
    db_session.add_all(books_lst)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{user.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": user.id,
        "first_name": default_seller["first_name"],
        "last_name": default_seller["last_name"],
        "email": default_seller["email"],
        "books": [
            {
                "id": books_lst[i].id,
                "title": default_book["title"],
                "author": default_book["author"],
                "year": default_book["year"],
                "count_pages": default_book["count_pages"]
            }
            for i in range(n)
        ]
    }


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    user = seller.Seller(**default_seller)
    db_session.add(user)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{user.id}",
        json={"id": user.id, "first_name": "Misha", "last_name": "Ivanov", "email": "example@mail.com"}
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(seller.Seller, user.id)
    assert res.first_name == "Misha"
    assert res.last_name == "Ivanov"
    assert res.email == "example@mail.com"
    assert res.id == user.id
