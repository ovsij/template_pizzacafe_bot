from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import httplib2
import pandas as pd
from random import randint, sample
import requests
import os

from database.db import *

# User
@db_session
def register_user(telegram_user) -> User:
    if not User.exists(tg_id = str(telegram_user.id)):
        user = User(
            tg_id=str(telegram_user.id), 
            username=telegram_user.username, 
            first_name=telegram_user.first_name, 
            last_name=telegram_user.last_name)
        flush()
        return user
    else:
        print(f'User {telegram_user.id} exists')

@db_session
def get_user(telegram_user) -> User:
    return User.get(tg_id=str(telegram_user.id))

@db_session
def get_users() -> list:
    return User.select(int(u.tg_id) for u in User)[:]
        
@db_session()
def update_user(
    tg_id : str, 
    username : str = None,
    first_name : str = None,
    last_name : str = None,
    phone : str = None,
    address : str = None,
    orders : Order = None,
    last_usage : bool = None,
    is_banned : bool = None
    ) -> User:

    user_to_update = User.get(tg_id = tg_id)
    if username:
        user_to_update.username = username
    if first_name:
        user_to_update.first_name = first_name
    if last_name:
        user_to_update.last_name = last_name
    if phone:
        user_to_update.phone = phone
    if address:
        user_to_update.address = address
    if is_banned:
        user_to_update.is_banned = is_banned
    if is_banned == False:
        user_to_update.is_banned = is_banned
    if orders:
        user_to_update.orders = orders
    if last_usage:
        user_to_update.last_usage = datetime.now()
    return user_to_update

# Product
@db_session()
def update_product(
    product : Product,
    name : str = None, 
    active : bool = None, 
    category : bool = None, 
    sub_category : str = None, 
    description : str = None, 
    weight : int = None, 
    stock : int = None, 
    price : float = None, 
    image : str = None, 
    link : str = None) -> Product:
    product_to_upd = product
    if name:
        product_to_upd.name = name
    if active:
        product_to_upd.active = active
    if category:
        product_to_upd.category = category
    if sub_category:
        product_to_upd.sub_category = sub_category
    if description:
        product_to_upd.description = description
    if weight:
        product_to_upd.weight = weight
    if stock:
        product_to_upd.stock = stock
    if price:
        product_to_upd.price = price
    if image:
        product_to_upd.image = image
    if link:
        product_to_upd.link = link
    return product_to_upd

@db_session()
def create_product(
    name : str, 
    active : bool = None, 
    category : bool = None, 
    sub_category : str = None, 
    description : str = None, 
    weight : int = None, 
    stock : int = None, 
    price : float = None, 
    image : str = None, 
    link : str = None) -> Product:
    product = Product(name=name)

    update_product(
        product=product,
        active=active,
        category=category,
        sub_category=sub_category,
        description=description,
        weight=weight,
        stock=stock,
        price=price,
        image=image,
        link=link
    )
    return product

@db_session()
def get_categories():
    return select(p.category for p in Product)[:]

@db_session()
def get_sub_categories(category_id : int):
    return select(p.sub_category for p in Product if p.category.id == category_id)[:]

@db_session()
def get_product_by_id(id : id):
    return Product[id]

@db_session()
def get_products_by_category(category : int):
    return select(p for p in Product if p.category.id == category and p.active)[:]

@db_session()
def get_products_by_subcategory(category : int, sub_category : int):
    return select(p for p in Product if p.sub_category.id == sub_category and p.category.id == category and p.active)[:]

@db_session()
def get_products_by_order(order : Order):
    return select(p for p in OrderProduct if p.order == order)[:]

@db_session()
def get_image(prod_id : int):
    return Product[prod_id].image                

# Cart  
@db_session()
def add_to_cart(tg_id : str, prod_id: id, count: id) -> Cart:
    user = User.get(tg_id=tg_id)
    product = Product.get(id=prod_id)
    if not Cart.exists(user=user, product=product):
        cart = Cart(user=user, product=product, count=count)
    else:
        cart = update_cart(tg_id=tg_id, prod_id=prod_id, count=count)
    return cart

@db_session()
def get_cart(telegram_user):
    user = User.get(tg_id=str(telegram_user.id))
    return select(p for p in Cart if p.user == user)[:]

@db_session()
def update_cart(tg_id : str, prod_id : id, count: id):
    cart_to_update = Cart.get(user=User.get(tg_id=tg_id), product=Product[prod_id])
    cart_to_update.count = count
    return cart_to_update

@db_session()
def del_from_cart(id : int, tg_id : str):
    cart_to_delete = Cart.get(id=id, user=User.get(tg_id=tg_id))
    cart_to_delete.delete()

@db_session()
def clean_cart(telegram_user):
    cart_to_clean = get_cart(telegram_user)
    for p in cart_to_clean:
        p.delete()

@db_session()
def cart_exists(tg_id : str):
    user=User.get(tg_id=tg_id)
    return Cart.exists(user=user)


# Order
@db_session()
def create_order(
    tg_id : str,
    delivery_type : str,
    payment_type : str
    ) -> Order:
    user = User.get(tg_id=tg_id)
    order = Order(user=user, delivery_type=delivery_type, payment_type=payment_type)
    products = select([c.product, c.count] for c in Cart if c.user == user)[:]
    for product in products:
        OrderProduct(order=order, product=product[0], count=product[1])
    return order

@db_session()
def get_order(id : id):
    return Order[id]

@db_session()
def get_orders(tg_id : str):
    user = User.get(tg_id=tg_id)
    return select(o for o in Order if o.user == user)[:]

@db_session()
def update_order(
    id : int,
    delivery_type : str = None,
    payment_type : str = None,
    closed : bool = None) -> Order:
    order_to_update = Order.get(id=id)
    if delivery_type:
        order_to_update.delivery_type = delivery_type
    if payment_type:
        order_to_update.payment_type = payment_type
    if closed:
        order_to_update.closed = closed
    return Order

# Category
@db_session()
def get_category_by_id(id : int):
    return Category.get(id=id)

#SubCategory
@db_session()
def get_subcategory_by_id(id : int):
    return SubCategory.get(id=id)

#Создание демонстрационной базы данных
@db_session()
def import_test_db(tg_id : str):
    df = pd.read_excel('database/menu1.xlsx')
    
    try:
        os.mkdir(f'database/images/{tg_id}')
    except FileExistsError:
        pass

    for i in range(len(df)):
        if not Product.exists(name=df.iloc[i]['Наименование']):
            # скачиваем изображение
            h = httplib2.Http('.cache')
            response, content = h.request(df.iloc[i]['Картинка'])
            with open(f"database/images/{tg_id}/{df.iloc[i]['Наименование']}.jpeg", "wb") as file:
                file.write(content)

            # создаем продукт
            product = create_product(
                name=str(df.iloc[i]['Наименование']),
                active=bool(df.iloc[i]['Активно']),
                description=str(df.iloc[i]['Описание']),
                weight=str(df.iloc[i]['Вес, гр.']),
                stock=int(df.iloc[i]['Наличие']),
                price=float(df.iloc[i]['Цена']),
                image=f"database/images/{tg_id}/{df.iloc[i]['Наименование']}.jpeg",
                link=str(df.iloc[i]['Ссылка'])
                )
            
            if Category.exists(name=str(df.iloc[i]['Категория'])):
                update_product(product=product, category=Category.get(name=str(df.iloc[i]['Категория'])))
            else:
                update_product(product=product, category=Category(name=str(df.iloc[i]['Категория'])))
            if SubCategory.exists(name=str(df.iloc[i]['Подкатегория'])):
                update_product(product=product, sub_category=SubCategory.get(name=str(df.iloc[i]['Подкатегория'])))
            else:
                if str(df.iloc[i]['Подкатегория']) != "nan":
                    update_product(product=product, sub_category=SubCategory(name=str(df.iloc[i]['Подкатегория'])))

@db_session()
def create_demo_orders(tg_id : str = None):
    if not Order.exists(user=User.get(tg_id=tg_id)):
        user = User.get(tg_id=tg_id)
        dates = sorted([datetime.now() - timedelta(days=randint(0, 356), hours=randint(0, 24)) for _ in range(0, 25)])
        for date in dates:
            order = Order(
                user=user,
                datetime=date,
                delivery_type=sample(DeliveryType.list(), 1)[0],
                payment_type=sample(PaymentType.list(), 1)[0],
                status=sample(Status.list(), 1)[0],
            )
            products = sample(sorted(select(p for p in Product)[:]), randint(1, 10))
            print(products)
            [OrderProduct(order=order, product=product, count=randint(1, 5)) for product in products]

