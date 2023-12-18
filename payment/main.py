from fastapi import FastAPI
from redis_om import HashModel, get_redis_connection
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import os
import requests
import time
app=FastAPI()

redis=get_redis_connection(
    host="redis-10307.c295.ap-southeast-1-1.ec2.cloud.redislabs.com",
    port=10307,
    password='oDBhSIY23y52DPL0o9HPiK3mu3HECL80',
    decode_responses=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5000','http://localhost:4000'],
    allow_methods=['*'],
    allow_headers=['*']
)



class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str
    
    class Meta:
        database=redis

def format(pk:str):
    order=Order.get(pk)
    return {
        "product_id": order.pk,
        "price": order.price,
        "fee":order.fee,
        "total":order.total,
        "quantity":order.quantity,
        "status":order.status

    }


@app.get('/orders')
def all():
    return [format(_) for _ in Order.all_pks()if format(_)['status']=='completed']


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
    body= await request.json()


    req = requests.get('http://localhost:3000/products/{}'.format(body["id"]))
    product=req.json()
    order=Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.20*product['price'],
        total=product['price']*1.2,
        quantity=body['quantity'],
        status='pending'
        )
    order.save()
    background_tasks.add_task(order_completed, order)
    return order



@app.get('/orders/{pk}')
def get_order(pk :str):
    return Order.get(pk)


def order_completed(order: Order):
    order.status='completed'
    order.save()
    redis.xadd('order_completed', order.dict(),'*')
    return order


