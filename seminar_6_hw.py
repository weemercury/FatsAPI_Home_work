import databases
import sqlalchemy
import aiosqlite

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


DATABASE_URL = "sqlite:///mydatabase_1.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(32)),
    sqlalchemy.Column("second_name", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(128)),
)

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(15)),
    sqlalchemy.Column("description", sqlalchemy.String(100)),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column("goods_id", sqlalchemy.ForeignKey('goods.id')),
    sqlalchemy.Column("date", sqlalchemy.DateTime),
    sqlalchemy.Column('status', sqlalchemy.Boolean)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

app = FastAPI()


class UserIn(BaseModel):
    first_name: str = Field(max_length=32)
    second_name: str = Field(max_length=32)
    email: EmailStr = Field(max_length=128)
    password: str = Field(max_length=128)

class UserID(UserIn):
    id: int
    
    
class Goods(BaseModel):
    title: str = Field(max_length=32)
    description: str = Field(max_length=256)
    price: float = Field(ge=1)

class GoodsID(Goods):
    id: int
    
    
class Orders(BaseModel):
    date: datetime
    status: bool
    user_id: int
    goods_id: int
    
class OrdersID(Orders):
    id: int
    
    

@app.on_event("startup")
async def startup():
    await database.connect()
    
    
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    

# Users
@app.get('/users/', response_model=List[UserID])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=UserID)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.post('/users/', response_model=UserID)
async def create_user(user: UserIn):
    query = users.insert().values(first_name = user.first_name, 
                                  second_name = user.second_name,
                                  email = user.email, 
                                  password = user.password
                                  )
    last_record_id = await database.execute(query)
    return {**user.dict(), 'id': last_record_id}


@app.put('/users/{user_id}', response_model=UserID)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), 'id': user_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted!'}



# GOODS
@app.get('/goods/', response_model=List[GoodsID])
async def get_goods():
    query = goods.select()
    return await database.fetch_all(query)


@app.get('/goods/{good_id}', response_model=GoodsID)
async def get_good(good_id: int):
    query = goods.select().where(goods.c.id == good_id)
    return await database.fetch_one(query)


@app.post('/goods/', response_model=GoodsID)
async def create_good(good: Goods):
    query = goods.insert().values(title = good.title, 
                                  description = good.description,
                                  price = good.price, 
                                  )
    last_record_id = await database.execute(query)
    return {**good.dict(), 'id': last_record_id}


@app.put('/goods/{good_id}', response_model=GoodsID)
async def update_good(good_id: int, new_good: Goods):
    query = goods.update().where(goods.c.id == good_id).values(**new_good.dict())
    await database.execute(query)
    return {**new_good.dict(), 'id': good_id}


@app.delete('/goods/{good_id}')
async def delete_good(good_id: int):
    query = goods.delete().where(goods.c.id == good_id)
    await database.execute(query)
    return {'message': 'One of Goods are deleted!'}



# ORDERS
@app.get('/orders/', response_model=List[OrdersID])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/orders/{order_id}', response_model=OrdersID)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.post('/orders/', response_model=OrdersID)
async def create_order(order: Orders):
    query = orders.insert().values(date = order.date, 
                                  status = order.status, 
                                  user_id = order.user_id,
                                  goods_id = order.goods_id
                                  )  
    last_record_id = await database.execute(query)
    return {**order.dict(), 'id': last_record_id}


@app.put('/orders/{order_id}', response_model=OrdersID)
async def update_order(order_id: int, new_order: Orders):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), 'id': order_id}


@app.delete('/orders/{order_id}')
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order are deleted!'}