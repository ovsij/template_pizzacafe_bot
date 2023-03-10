from aiogram import types


from loader import dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *

# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def btn_callback(callback_query: types.CallbackQuery):
    code = callback_query.data.split('_')
    print(f'User {callback_query.from_user.id} open {code}')

    if code[1] == 'menu':
        text, reply_markup = inline_kb_menu(callback_query.from_user)
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )

    if code[1] == 'catalog':
        text, reply_markup = inline_kb_categories(page=int(code[-1]))
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )
    
    if code[1] == 'category':
        text, reply_markup = inline_kb_subcategories(category=int(code[2]), page=int(code[-1]))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'subcategory':
        text, reply_markup = inline_kb_products(category=int(code[2]), sub_category=int(code[3]), page=int(code[-1]))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'product':
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[-1]))
        try:
            media = types.InputMedia(media=open(get_image(int(code[-1])), 'rb'), caption=text)
            await callback_query.message.edit_media(media=media, reply_markup=reply_markup)
            #await callback_query.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode=types.ParseMode.MARKDOWN)
        except Exception as ex:
            await callback_query.message.delete()
            photo = types.InputFile(get_image(int(code[-1])))
            await bot.send_photo(
                callback_query.message.chat.id, 
                photo=photo, 
                caption=text, 
                reply_markup=reply_markup
            )
        
    if code[1] == 'count':
        if code[3] == 'plus':
            counter = int(code[-1]) + 1
        elif code[3] == 'minus' and int(code[-1]) > 1:
            counter = int(code[-1]) - 1
        else:
            return
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[2]), counter=counter)
        await callback_query.message.edit_caption(caption=text, reply_markup=reply_markup)

    if code[1] == 'tocart':
        if callback_query.message.caption.split(' ')[-1] == 'корзину!':
            return
        add_to_cart(tg_id=str(callback_query.from_user.id), prod_id=int(code[2]), count=int(code[-1]))
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[2]))
        text += '\n\nТовар успешно добавлен в корзину!'
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup
        )

    if code[1] == 'cart':
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )

    if code[1] == 'delete':
        del_from_cart(id=code[-1], tg_id=str(callback_query.from_user.id))
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'deleteall':
        clean_cart(callback_query.from_user)
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'orders':
        if int(code[-1]) > 0:
            page = int(code[-1])
        else:
            page = 1
        text, reply_markup = inline_kb_orders(callback_query.from_user, page=page)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'order':
        text, reply_markup = inline_kb_order(callback_query.from_user, id=int(code[2]), page=int(code[-1]))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'terms':
        text, reply_markup = inline_kb_terms(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'contact':
        text, reply_markup = inline_kb_contact()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'settings':
        text, reply_markup = inline_kb_settings(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'change':
        if code[-1] == 'phone':
            await Form.user_phone.set()
            text, reply_markup = reply_kb_change(param='phone')
            Form.prev_message = await bot.send_message(
                callback_query.from_user.id, 
			    text = text,
                reply_markup=reply_markup)
        if code[-1] == 'address':
            await Form.user_address.set()
            text = reply_kb_change(param='address')
            Form.prev_message = await bot.send_message(
                callback_query.from_user.id, 
			    text = text,
            )