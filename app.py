from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import databases
import sqlalchemy


# Модель для товаров
class ItemIn(BaseModel):
    name: str
    description: str
    price: float


class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float


# Модель для заказов
class OrderIn(BaseModel):
    user_id: int
    item_id: int
    order_date: str
    status: str


class Order(BaseModel):
    id: int
    user_id: int
    item_id: int
    order_date: datetime
    status: str


# Модель для пользователей
class UserIn(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str


class User(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    password: str


DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

items = sqlalchemy.Table("items", metadata,
                         sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
                         sqlalchemy.Column('name', sqlalchemy.String(32)),
                         sqlalchemy.Column("description", sqlalchemy.String(128)),
                         sqlalchemy.Column("price", sqlalchemy.Float)
                         )

orders = sqlalchemy.Table("orders", metadata,
                          sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
                          sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
                          sqlalchemy.Column("item_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('items.id')),
                          sqlalchemy.Column("order_date", sqlalchemy.DateTime),
                          sqlalchemy.Column("status", sqlalchemy.String(32))
                          )

users = sqlalchemy.Table("users", metadata,
                         sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
                         sqlalchemy.Column('firstname', sqlalchemy.String(32)),
                         sqlalchemy.Column("lastname", sqlalchemy.String(32)),
                         sqlalchemy.Column("email", sqlalchemy.String(128)),
                         sqlalchemy.Column("password", sqlalchemy.String(128)),
                         )

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/items/", response_model=Item)
async def create_item(item: ItemIn):
    query = items.insert().values(name=item.name, description=item.description, price=item.price)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}


@app.get("/items/", response_model=List[Item])
async def read_items():
    query = items.select()
    return await database.fetch_all(query)


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    query = items.select().where(items.c.id == item_id)
    return await database.fetch_one(query)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, new_item: ItemIn):
    query = items.update().where(items.c.id == item_id).values(**new_item.dict())
    await database.execute(query)
    return {**new_item.dict(), "id": item_id}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)
    return {'message': 'Item deleted'}


@app.post("/orders/", response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(user_id=order.user_id, item_id=order.item_id,
                                   order_date=datetime.strptime(order.order_date, '%Y-%m-%d'), status=order.status)
    last_record_id = await database.execute(query)
    return {**order.dict(), "id": last_record_id}


@app.get("/orders/", response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == order_id)\
        .values(user_id=new_order.user_id, item_id=new_order.item_id,
                order_date=datetime.strptime(new_order.order_date, '%Y-%m-%d'), status=new_order.status)
    await database.execute(query)
    return {**new_order.dict(), "id": order_id}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order deleted'}


@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(firstname=user.firstname, lastname=user.lastname,
                                  email=user.email, password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}
