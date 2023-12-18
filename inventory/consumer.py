from main import Product,redis
import time



key='order_completed'
group='inventory-group'


try:
    redis.xgroup_create(key,group)
except:
    print("Group already exists!")


while True:
    try:
        results = redis.xreadgroup(group,key,{key: '>'},None)
        if results:
            for result in results:
                order_deet=result[1][0][1]
                print(order_deet)
                print(order_deet['product_id'])
                product=Product.get(order_deet['product_id'])
                print("PRODUCT OBJ: ", product)
                product.quantity=product.quantity-int(order_deet['quantity'])
                print(product.quantity)
                product.save()
    except Exception as e:
       print(e)


    time.sleep(1)