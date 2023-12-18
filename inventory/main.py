from fastapi import FastAPI
from redis_om import HashModel, get_redis_connection
from fastapi.middleware.cors import CORSMiddleware

import os
app=FastAPI()

redis=get_redis_connection(
    host="redis-10307.c295.ap-southeast-1-1.ec2.cloud.redislabs.com",
    port=10307,
    password='oDBhSIY23y52DPL0o9HPiK3mu3HECL80',
    decode_responses=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5000'],
    allow_methods=['*'],
    allow_headers=['*']
)



class Product(HashModel):
    name: str
    quantity: int
    price: float


    class Meta:
        database=redis




def format(pk: str):
    product = Product.get(pk)
    return {
        'id' : product.pk,
        'name' : product.name,
        'price' : product.price,
        'quantity' : product.quantity
    }



@app.get('/products')
def all():
    return [format(_) for _ in Product.all_pks()]





@app.post('/products')
def create(product: Product):
    return product.save()

@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete_product(pk: str):
    return Product.delete(pk)
    

@app.put("/products/{pk}")
def update_(pk: str, up_dict: dict):
    product=Product.get(pk)
    for i in up_dict:
        if 'pk' not in i:
            product.__dict__[i]=up_dict[i] 
    return product.save()
        
        
    