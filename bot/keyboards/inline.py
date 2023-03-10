from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
from dotenv import load_dotenv
import os

load_dotenv()

from .buttons import *
from .constructor import InlineConstructor
from bot.loader import bot
from database.crud import *


def inline_kb_menu(telegram_user):
    user = get_user(telegram_user)
    # исключаем None
    last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0]
    phone = [phone for phone in [user.phone, '\n--укажите в настройках--'] if phone][0]
    address = [address for address in [user.address, '\n--укажите в настройках--'] if address][0]
    text = markdown.text(
        'ГЛАВНОЕ МЕНЮ',
        'Добро пожаловать в службу оформления онлайн заказов кафе "Темпура".',
        'Вы можете посмотреть наше меню в каталоге и добавить желаемые позиции в корзину.',
        'Мы доставим заказ по вашему адресу или вы можете забрать его сами по адресу: 3-я улица Строителей, 25, офис 11',
        f'\nИмя: \n{user.first_name} {last_name}',
        f'\nТелефон: {phone}',
        f'\nАдрес доставки: {address}',
        sep='\n')

    text_and_data = [
        [emojize(':closed_book: Каталог', language='alias'), 'btn_catalog_1'],
        [emojize(':shopping_bags: Корзина', language='alias'), 'btn_cart'],
        [emojize(':package: Мои заказы', language='alias'), 'btn_orders_1'],
        [emojize(':telephone: Контакты', language='alias'), 'btn_contact'],
        [emojize(':question: Условия', language='alias'), 'btn_terms'],
        [emojize(':gear: Настройки', language='alias'), 'btn_settings'],
    ]
    schema = [1, 2, 2, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_categories(page : int = 1):
    #выводит названия категорий, если их нет выводит продукты
    text = 'КАТАЛОГ'
    categories = get_categories()
    text_and_data = []
    schema = []
    if bool(categories):
        text += '\n\nВыберите категорию'
        for cat in categories:
            text_and_data.append([f'{cat.name}', f'btn_category_{cat.id}_1'])
            schema.append(1)
        
        if len(categories) > 10:
            text_and_data, schema = btn_prevnext(len(categories), text_and_data, schema, page, name='catalog')
        
        text_and_data.append(btn_back('menu'))
        schema.append(1)
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        return inline_kb_products()
    
def inline_kb_subcategories(category : int = None, page : int = 1):
    #выводит названия суб-категорий, если их нет выводит продукты
    text = f'КАТАЛОГ\n\n{get_category_by_id(category).name}'
    sub_categories = get_sub_categories(category_id=category)
    text_and_data = []
    schema = [1]
    if sub_categories:
        for sc in sub_categories:
            text_and_data.append([f'{sc.name}', f'btn_subcategory_{category}_{sc.id}_1'])
            schema.append(1)
        if len(sub_categories) > 10:
            text_and_data, schema = btn_prevnext(len(sub_categories), text_and_data, schema, page, name=f'subcategory_{category}')

        text_and_data.append(btn_back(f'catalog_1'))
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        return inline_kb_products(category=category, page=page)
    
def inline_kb_products(category : int = None, sub_category : int = None, page : int = 1):
    text = 'КАТАЛОГ'
    if sub_category == None:
        text += f'\n\n{get_category_by_id(category).name}'
        products = get_products_by_category(category=category)
        btn_prevnext_name = f'category_{category}'
    else:
        text += f'\n\n{get_subcategory_by_id(sub_category).name}'
        products = get_products_by_subcategory(category=category, sub_category=sub_category)
        btn_prevnext_name = f'category_{category}_{sub_category}'
    text_and_data = []
    schema = []
    if bool(products):
        for p in products:
            text_and_data.append([f'{p.name}', f'btn_product_{p.id}'])
            schema.append(1)
    else:
        text += '\n\n К сожалению, на данный момент в этой категории ничего нет'
    if len(products) > 10:
        text_and_data, schema = btn_prevnext(len(products), text_and_data, schema, page, name=btn_prevnext_name)
    if sub_category != None:
        text_and_data.append(btn_back(f'category_{category}_1'))
    else:
        text_and_data.append(btn_back(f'catalog_1'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_product(tg_id : str, id : int, counter : int = 1):
    product = get_product_by_id(id)
    if product.sub_category:
        products = get_products_by_subcategory(category=product.category.id, sub_category=product.sub_category.id)
    else:
        products = get_products_by_category(category=product.category.id)
    text = f'{product.name}\n\n{product.description}\n\nВес: {product.weight} гр.\n\nЦена: {round(product.price * counter, 2)} руб.'
    products_id = [p.id for p in products]
    back = products_id[products_id.index(id) - 1]
    if products_id.index(id) == len(products) - 1:
        next = products_id[0]
    else:
        next = products_id[products_id.index(id) + 1]

    text_and_data = [
        [emojize(':small_red_triangle:', language='alias'), f'btn_count_{id}_plus_{counter}'],
        [emojize(f'{counter} шт.', language='alias'), f'btn_pass'],
        [emojize(':small_red_triangle_down:', language='alias'), f'btn_count_{id}_minus_{counter}'],
        [emojize(':shopping: Добавить в корзину', language='alias'), f'btn_tocart_{id}_{counter}'],
        [emojize(':arrow_backward:', language='alias'), f'btn_product_{back}'],
        [f'[{products_id.index(id) + 1} из {len(products)}]', f'btn_pass'],
        [emojize(':arrow_forward:', language='alias'), f'btn_product_{next}'],
        [emojize(':leftwards_arrow_with_hook: В каталог', language='alias'), 'btn_catalog_1']
    ]
    schema = [1, 1, 1, 1, 3, 1]
    if cart_exists(tg_id):
        text_and_data.append([emojize(':shopping: Корзина', language='alias'), f'btn_cart'])
        schema[-1] = 2
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

async def inline_kb_cart(telegram_user):
    text = 'КОРЗИНА\n'
    text_and_data = []
    schema = []
    cart = get_cart(telegram_user)
    prices = []
    sum = 0
    for p in cart:
        product = get_product_by_id(p.product.id)
        sum += product.price * p.count
        text += f'\n{cart.index(p) + 1}. {product.name} \n    ({round(product.price, 2)} р. * {p.count} шт.)'
        text_and_data.append([emojize(f':x: {product.name} | {p.count} шт.', language='alias'), f'btn_delete_{p.id}'])
        schema.append(1)
        prices.append(types.LabeledPrice(label=f'{product.name} | {p.count} шт.', amount=int(product.price * p.count * 100)))
    
    if not cart:
        text += '\nКорзина пуста...'
        button_type = None
    else:
        text += f'\n\nИтого: {round(sum, 2)} руб.'
        text_and_data.append([emojize(f':x: Очистить корзину', language='alias'), f'btn_deleteall'])
        schema.append(1)
        button_type = []
        for i in range(len(text_and_data)):
            button_type.append('callback_data')
        link = await bot.create_invoice_link(title='Заказ', description='Оформление заказа', payload='test',
            provider_token=os.getenv('provider_token'), currency='rub', 
            prices=prices, 
            need_name=True, need_phone_number=True, need_email=True, need_shipping_address=True)
        text_and_data.append([emojize(f':white_check_mark: Оформить заказ', language='alias'), link])
        button_type.append('url')
        schema.append(1)
        button_type.append('callback_data')
    
    text_and_data.append([emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu'])
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema, button_type)
    return text, inline_kb

def inline_kb_orders(telegram_user, page : int):
    text = 'ИСТОРИЯ ЗАКАЗОВ'
    orders = get_orders(tg_id=str(telegram_user.id))
    if not orders:
        text += '\n\nВы еще ничего не заказывали...'
    text_and_data = []
    schema = []
    for order in orders:
        if order.status == 'Доставлен':
            emoji_status = ':white_check_mark:'
        elif order.status == 'Отменен':
            emoji_status = ':x:'
        elif order.status == 'В обработке':
            emoji_status = ':recycle:'
        text_and_data.append([emojize(f'{order.datetime.date()} {emoji_status} {order.status}', language='alias'),f'btn_order_{order.id}_{page}'])
        schema.append(1)
    if len(orders) > 10:
        text_and_data, schema = btn_prevnext(len(orders), text_and_data, schema, page, 'orders')
    text_and_data.append([emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu'])
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_order(telegram_user : dict, id : int, page : int):
    order = get_order(id=id)
    text = markdown.text(
        f'ЗАКАЗ № {id}',
        '\n'
        f'Дата:                 {order.datetime.date()}',
        f'Время:              {order.datetime.strftime("%H:%M")}',
        f'Вид доставки: {order.delivery_type}',
        f'Вид оплаты:     {order.payment_type}',
        f'Статус:              {order.status}\n\n', 
        'Содержимое заказа:\n', sep='\n')
    products = get_products_by_order(order)
    counter = 1
    sum = 0
    for p in products:
        product = get_product_by_id(id=p.product.id)
        text += f'{counter}. {product.name} \n    ({round(product.price, 2)} р. * {p.count} шт.)\n'
        counter += 1
        sum += product.price * p.count
    text += f'\nИтого: {round(sum, 2)} руб.'
    text_and_data = [
        [emojize(':arrow_backward: К заказам', language='alias'), f'btn_orders_{page}'],
        [emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu']
    ]
    schema = [1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_terms(tg_id):
    text = markdown.text(
        'УСЛОВИЯ ДОСТАВКИ И ОПЛАТЫ',
        '',
        'Мы работаем каждый день с 10:00 до 20:00',
        'Вы можете оплатить заказ как через телеграм оплату, так и наличными при самовывозе',
        '',
        'Контактный телефон:',
        '8800xxxxxxxxx',
        sep='\n'
    )
    text_and_data = [
        btn_back('menu')
    ]
    schema = [1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_contact():
    text = markdown.text(
        'КОНТАКТЫ',
        'У нас можно заказать бота для:',
        '- Магазинов оптовой и розничной торговли',
        '- Кафе, кондитерских и фастфудов',
        '- Онлайн и офлайн бизнеса',
        '- Любые иные цели по вашему запросу',
        '',
        'Мы предоставляем:',
        '- Удобное меню бота',
        '- Походящий формат административной панели',
        '- Индивидуальный подход к каждому клиенту',
        '- Предсказуемые сроки работы',
        sep='\n'
        )
    text_and_data = [
        ['Заказать бота', 't.me/v3talik'],
        btn_back('menu')
    ]
    schema = [1, 1]
    button_type = ['url', 'callback_data']
    inline_kb = InlineConstructor.create_kb(text_and_data, schema, button_type)
    return text, inline_kb

def inline_kb_settings(telegram_user):
    user = get_user(telegram_user)
    # исключаем None
    last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0]
    phone = [phone for phone in [user.phone, '\n--укажите в настройках--'] if phone][0]
    address = [address for address in [user.address, '\n--укажите в настройках--'] if address][0]
    text = markdown.text(
        'НАСТРОЙКИ',
        f'\nИмя: \n{user.first_name} {last_name}',
        f'\nТелефон: {phone}',
        f'\nАдрес доставки: {address}',
        sep='\n')
    text_and_data = [
        ['Изменить телефон', 'btn_change_phone'],
        ['Изменить адрес', 'btn_change_address'],
        btn_back('menu')
    ]
    schema = [1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb


