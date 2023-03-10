from datetime import datetime
from decimal import Decimal
from enum import Enum
from pony.orm import *

db = Database()

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class DeliveryType(ExtendedEnum):
    DELIVERY = 'Доставка'
    PICKUP = 'Самовывоз'

class PaymentType(ExtendedEnum):
    ONLINE = 'Онлайн оплата'
    CASH = 'Наличными'

class Status(ExtendedEnum):
    DELIVERED = 'Доставлен'
    PROCESS = 'В обработке'
    CANCELED = 'Отменен'


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_id = Optional(str)
    username = Optional(str, unique=True)
    first_name = Optional(str, nullable=True)
    last_name = Optional(str, nullable=True)
    phone = Optional(str, nullable=True)
    address = Optional(str, nullable=True)
    carts = Set('Cart')
    orders = Set('Order')
    first_usage = Optional(datetime, default=lambda: datetime.now())
    last_usage = Optional(datetime, default=lambda: datetime.now())
    is_banned = Optional(bool, default=False)


class Cart(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required('Product')
    count = Optional(int, default=1)


class Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    active = Optional(bool, default=True)
    category = Optional('Category')
    sub_category = Optional('SubCategory')
    description = Optional(str, nullable=True)
    weight = Optional(str, nullable=True)
    stock = Optional(int, unsigned=True)
    price = Optional(float)
    image = Optional(str, nullable=True)
    link = Optional(str, nullable=True)
    carts = Set(Cart)
    order_products = Set('OrderProduct')


class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    product = Set(Product)


class SubCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    product = Set(Product)


class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    datetime = Optional(datetime, default=lambda: datetime.now())
    delivery_type = Optional(str, nullable=True)
    payment_type = Optional(str, nullable=True)
    status = Optional(str, nullable=True)
    order_products = Set('OrderProduct')


class OrderProduct(db.Entity):
    id = PrimaryKey(int, auto=True)
    order = Required(Order)
    product = Required(Product)
    count = Optional(int, default=1)
