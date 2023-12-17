from fastapi import FastAPI
from redis_om import HashModel, get_redis_connection
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import os
import requests
import time
app=FastAPI()

redis=get_redis_connection(
    host="127.0.0.1",
    port=8000,
    password='raghib',
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
async def create(request: Request):
    body= await request.json()


    req = requests.get('http://localhost:4000/products/{}'.format(body["id"]))
    product=req.json()
    order=Order(product_id=body['id'],price=product['price'],fee=0.20*product['price'],total=product['price']*1.2,quantity=body['quantity'],status='pending')
    order.save()
    await order_completed(order)
    return order



def order_completed(order: Order):
    time.sleep(3)
    key=order.product_id
    req=requests.get('http://localhost:4000/products/{}'.format(key)).json()
    if req['quantity']>order.quantity:
        
        


