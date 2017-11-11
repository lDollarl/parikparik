#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import messages
import db_api
import time
import functions
import requests
import random
import ast
import settings
import flask
import threading
import qiwi
from yandex_money import api


# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

users_menu = {}
bans={}
tb = telebot.TeleBot(settings.telegram_token,threaded=True)
bot_info = tb.get_me()
repost_message = None
answ=functions.AnswFunctions(tb=tb,db=db_api)
helpers = functions.helpers()
wallet = api.Wallet(access_token=settings.ya_token)

to_replace = {'%all_users%': lambda: db_api.count.users(),
              '%users_today%': lambda: db_api.count.activity(date=time.strftime("%d/%m/%Y")),
              '%posts_count%': lambda: db_api.count.channels(active=1),
              '%money_for_views%': lambda: list(db_api.sumof.transactions(row='count', type='view_pay'))[0][
                  'sum(count)'],
              '%money_out%': lambda: list(db_api.sumof.transactions(row='count', type='pay_out'))[0]['sum(count)']}

def get_user(id,message):
    for i in range(1,6):
        user = db_api.get.users(user_id=id)
        if len(user) > 0:
            return user[0]
    try:
        tb.send_message(chat_id=message.chat.id, text='Чтобы начать - напиши /start')
    except:
        return False
    return False

def send_message(message,mobj,**kwargs):
    try:
        if 'text' in mobj: text = mobj['text']
        else: text = ' '

        if 'markup' in mobj: markup = answ.gen(mobj['markup'])
        else: return tb.send_message(message.chat.id, text=text,**kwargs)
        if message.from_user.id in settings.admins:
            markup = answ.gen(mobj['markup'])
            try:
                markup.row(types.KeyboardButton('Админка'))
            except:
                pass
        return tb.send_message(message.chat.id, text=text, reply_markup=markup, **kwargs)
    except:
        return


@tb.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id in settings.admins:
        send_message(message, messages.admin)
        user = db_api.get.users(user_id=message.from_user.id)
        db_api.insert.users(user_id=message.from_user.id,menu='admin')
        return
    else:
        return send_message(message, messages.admin['error'])

#  тут у нас спряталась работа с пересылом

# @tb.message_handler(content_types=["text",'channel','forward_from','post','sticker','forward_from_chat','audio','photo','video_note','voice','location','caption','game','sticker','document','venue','video','contact','entities','photo'],func= lambda m: m.forward_from_chat is not None)
# def nuks(message):
#
#     if message.forward_from_chat.type=='channel':
#
#
#         user = get_user(message.from_user.id, message)
#
#         if not user:
#             return
#         try:
#             add_info = ast.literal_eval(db_api.get.users(user_id=message.from_user.id)[0]['add_info'])
#         except:
#             add_info = {}
#
#         if message.from_user.id not in users_menu:
#
#             menu = user['menu']
#         else:
#             menu = users_menu[message.from_user.id]
#         user = user
#
#         if menu=='advert':
#             print(message)
#             try:
#                 channels = db_api.get.channels(channel_name='@' + message.forward_from_chat.username)
#             except:
#
#                 tb.send_message(message.chat.id,text=messages.for_advert['error_not_admin']['text'],reply_markup=answ.gen_inl(messages.for_advert['error_not_admin']['markup']))
#                 return
#             if len(channels)>0:
#
#                 if not channels[0]['active'] and message.from_user.id==channels[0]['user_id']:
#                     pass
#                 else:
#
#                     return send_message(message,messages.for_advert['already_in'])
#
#             add_info.update(
#                 {'channel_name': '@' + message.forward_from_chat.username, 'channel_id': message.forward_from_chat.id})
#             db_api.insert.users(user_id=message.from_user.id, add_info=str(add_info))
#             admin = answ.chechk_admin('@'+message.forward_from_chat.username,bot_info.username)
#             if admin:
#                 send_message(message,messages.for_advert['success'])
#
#                 db_api.insert.users(user_id=message.from_user.id,menu='advert_enter_cost')
#                 return
#             else:
#                 tb.send_message(message.chat.id,text=messages.for_advert['error_not_admin']['text'],reply_markup=answ.gen_inl(messages.for_advert['error_not_admin']['markup']))
#                 return
#         else:
#             return







@tb.message_handler(content_types=["text",'channel','forward_from','post','sticker','forward_from_chat','audio','photo','video_note','voice','location','caption','document'])
def nuka(message):
    if message.from_user.id in settings.admins:
       pass
    else:
        return send_message(message, messages.admin['error'])

    user_id = message.from_user.id
    global repost_message
    text = message.text
    user = get_user(message.from_user.id, message)

    if not user:
        return
    try:
        add_info = ast.literal_eval(db_api.get.users(user_id=message.from_user.id)[0]['add_info'])
    except:
        add_info = {}

    if message.from_user.id not in users_menu:

        menu = user['menu']
    else:
        menu=users_menu[message.from_user.id]


    if text=='⛔️ Отмена':
        db_api.insert.users(user_id=user['user_id'],menu='home')
        users_menu.update({message.from_user.id:'home'})
        send_message(message,messages.admin)
        return

    if text == 'заявки на вывод':
        tb.send_message(chat_id=message.chat.id, text='Заявки на вывод:', reply_markup=answ.inline_requests(page_n=1))
        return
    if text == 'модерация':
        tb.send_message(chat_id=message.chat.id, text='Каналы в базе:', reply_markup=answ.inline_channels(page_n=1))
        return
    if text == 'изменить баланс':
        db_api.insert.users(user_id=message.from_user.id, menu='enter_username')
        users_menu.update({message.from_user.id:'enter_username'})
        send_message(message,messages.edit_balance)
        return
    if text == 'пополнить баланс':
        db_api.insert.users(user_id=message.from_user.id, menu='enter_username_pay')
        users_menu.update({message.from_user.id:'enter_username_pay'})
        send_message(message,messages.edit_balance)
        return
    if text == 'сделать рассылку':
        db_api.insert.users(user_id=message.from_user.id, menu='enter_message')
        users_menu.update({message.from_user.id:'enter_message'})
        send_message(message,messages.mailer)
        return
    if menu == 'enter_message':
        repost_message=message
        db_api.insert.users(user_id=user['user_id'], menu='repost_message_success')
        users_menu.update({message.from_user.id: 'repost_message_success'})
        return send_message(message, messages.mailer['confirm'])
    if menu == 'repost_message_success':
        if text == '✅ Подтвердить':
            if repost_message is not None:
                threading.Thread(target=answ.mailer, kwargs={'message': repost_message}).start()
                db_api.insert.users(user_id=message.from_user.id, menu='admin')
                users_menu.update({message.from_user.id: 'admin'})
                return send_message(message, messages.mailer['success'])



                    # Просим стоимость
    if user['menu'] == 'enter_username':
        id = helpers.ifloat(text)
        if id:
            user_to=db_api.get.users(user_id=id)
            if len(user_to)<1:
                return send_message(message,messages.edit_balance['err_user'])
            msf = {}
            msf.update(messages.edit_balance['enter_balance'])
            msf['text'] = msf['text'].replace('%balance%', str(user_to[0]['balance']))

            send_message(message, msf)
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'user_id': id})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_id')
            users_menu.update({message.from_user.id: 'enter_balance_id'})
            return
        else:
            if '@' in text:
                text = text.replace('@','')
                user_to = db_api.get.users(username=text)
                if len(user_to) < 1:
                    return send_message(message, messages.edit_balance['err_user'])
                msf = {}
                msf.update(messages.edit_balance['enter_balance'])
                msf['text']=msf['text'].replace('%balance%',str(user_to[0]['balance']))

                send_message(message, msf)
                add_info = ast.literal_eval(user['add_info'])
                add_info.update({'user_id': text})
                add_info = str(add_info)
                db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name')
                users_menu.update({message.from_user.id: 'enter_balance_name'})
                return
            else:
                return send_message(message,messages.edit_balance['err_user'])

    if user['menu'] == 'enter_balance_name':
        id = helpers.ifloat(text)
        if id or id == 0.0:

            send_message(message, messages.edit_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            if isinstance(add_info['user_id'],str):
                user_id=db_api.get.users(username=add_info['user_id'])[0]['user_id']
                db_api.insert.users(user_id=user_id,balance=id)
            else:
                db_api.insert.users(user_id=add_info['user_id'], balance=id)
            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.edit_balance['err_number'])

    if user['menu'] == 'enter_balance_id':
        id = helpers.ifloat(text)
        if id:

            send_message(message, messages.edit_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            db_api.insert.users(user_id=add_info['user_id'],balance=id)
            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.edit_balance['err_number'])



  ############################

    if user['menu'] == 'enter_username_pay':
        id = helpers.ifloat(text)
        if id:
            user_to=db_api.get.users(user_id=id)
            if len(user_to)<1:
                return send_message(message,messages.pay_balance['err_user'])
            msf = {}
            msf.update(messages.pay_balance['enter_balance'])
            msf['text'] = msf['text'].replace('%balance%', str(user_to[0]['balance']))

            send_message(message, msf)
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'user_id': id})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name_pay')
            users_menu.update({message.from_user.id: 'enter_balance_name_pay'})
            return
        else:
            if '@' in text:
                text = text.replace('@','')
                user_to = db_api.get.users(username=text)
                if len(user_to) < 1:
                    return send_message(message, messages.pay_balance['err_user'])
                msf = {}
                msf.update(messages.pay_balance['enter_balance'])
                msf['text']=msf['text'].replace('%balance%',str(user_to[0]['balance']))

                send_message(message, msf)
                add_info = ast.literal_eval(user['add_info'])
                add_info.update({'user_id': text})
                add_info = str(add_info)
                db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name_pay')
                users_menu.update({message.from_user.id: 'enter_balance_name_pay'})
                return
            else:
                return send_message(message,messages.pay_balance['err_user'])

    if user['menu'] == 'enter_balance_name_pay':
        id = helpers.ifloat(text)
        if id or id ==0.0:

            send_message(message, messages.pay_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            if isinstance(add_info['user_id'],str):
                user_id=db_api.get.users(username=add_info['user_id'])
                answ.balance(type='pay_in', count=id, user=user_id[0])
            else:
                user_id = db_api.get.users(user_id=add_info['user_id'])
                answ.balance(type='pay_in', count=id, user=user_id[0])

            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.pay_balance['err_number'])


    if 'вчс' in text:
        try:
            print(text)
            chann_name=text.split(' ')[1]
            print(chann_name)
            db_api.insert.ban_channels(channel_name=chann_name)
            tb.send_message(chat_id=message.chat.id,text='Успешно!')
        except:
            tb.send_message(chat_id=message.chat.id, text='Проверьте имя канала.')

    if 'разбан' in text:
        try:
            print(text)
            user_name = text.split(' ')[1]

            s = db_api.get.ban_channels(channel_name=user_name)
            if len(s)>0:
                db_api.delete.ban_channels(channel_name=user_name)
                return tb.send_message(chat_id=message.chat.id, text='Успешно!')
            else:
                u = db_api.get.users(username=user_name.replace('@',''))
                if len(u)>0:
                    db_api.delete.ban_channels(channel_name=u[0]['user_id'])
                    return tb.send_message(chat_id=message.chat.id, text='Успешно!')
                else:
                    return tb.send_message(chat_id=message.chat.id, text='Не найден')
        except:
            tb.send_message(chat_id=message.chat.id, text='Проверьте имя пользователя.')

    if 'обнулить' in text:
        try:
            print(text)
            user_name = text.split(' ')[1]
            splitted = user_name.split(',')
            print(splitted)
            for i in splitted:
                s=db_api.get.users(username=i.replace('@',''))
                if len(s) > 0:
                    db_api.insert.users(user_id=s[0]['user_id'],balance=0,ref_balance=0)
                    requests.post('https://' + settings.WEBHOOK_HOST + ':8443/adminpost',
                                  json={'type': 'null_user', 'data': {'user_id': s[0]['user_id']}},
                                  verify=settings.WEBHOOK_SSL_CERT)
                    tb.send_message(chat_id=message.chat.id, text='Успешно! ' +i)
                else:

                    tb.send_message(chat_id=message.chat.id, text='Не найден '+i)
        except:
            tb.send_message(chat_id=message.chat.id, text='Проверьте имя пользователя.')

    if text == '📊 Статистика':
        obj = {}
        obj.update(messages.stat)

        for i in to_replace:
            obj['text']=obj['text'].replace(i,str(round((lambda x: x if x is not None else 0)(to_replace[i]()),2)))

        return send_message(message, obj,parse_mode='Markdown')




@tb.message_handler(content_types=["contact"])
def contact(message):
    text = message.text
    user = get_user(message.from_user.id, message)
    if not user:
        return


    if user['menu'] == 'enter_qiwi':
        add_info = ast.literal_eval(user['add_info'])
        add_info.update({'qiwi_number': message.contact.phone_number})
        answ.balance(type='pay_out',user=user,count=add_info['count_to_out_pay'],qiwi_number=message.contact.phone_number,username=message.from_user.username)
        db_api.insert.users(user_id=user['user_id'], menu='home',add_info=str(add_info))
        users_menu.update({message.from_user.id: 'home'})
        return send_message(message,messages.out_pay['success'])



@tb.callback_query_handler(lambda query: True)
def inl(query):
    data = query.data
    # try:

    user = get_user(query.from_user.id, query.message)

    if not user:
        return
    if 'declinec-' in data:
        channel = data.split('-')[1]

        requests.post('https://' + settings.WEBHOOK_HOST + ':8443/adminpost',
                      json={'type': 'delete_channel', 'data': {'channel': channel}}, verify=settings.WEBHOOK_SSL_CERT)
        time.sleep(2)
        db_api.delete.channels(channel_name=channel)
        return tb.edit_message_text(text='Удален', chat_id=query.message.chat.id, message_id=query.message.message_id)

    if 'acceptcid-' in data:
        channel = data.split('-')[1]
        db_api.insert.channels(channel_name=channel, mod=1)
        return tb.edit_message_text(text='Принят', chat_id=query.message.chat.id, message_id=query.message.message_id)
    if 'acceptid' in data:
        db_api.insert.transactions(trans_id=int(data.split('_')[1]),status='done')
        return tb.edit_message_text(text='Заявка принята',chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.inline_requests(1))

    if 'decline' in data:
        tr =  db_api.get.transactions(trans_id=int(data.split('_')[1]))
        user = db_api.get.users(user_id=tr[0]['user_id'])
        if len(user)>0:
            db_api.insert.users(user_id=tr[0]['user_id'],balance=user[0]['balance']+tr[0]['count'])
        db_api.insert.transactions(trans_id=int(data.split('_')[1]),status='decline')
        return tb.edit_message_text(text='Заявка отклонена',chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.inline_requests(1))

    if 'ban' in data:
        id = data.split('_')[1]
        print(bans)
        users = bans[id]
        for i in users:
            db_api.insert.ban_channels(channel_name=str(i))
        requests.post('https://'+settings.WEBHOOK_HOST+':8443/adminpost',json={'type':'ban','data':{'users':users}},verify=settings.WEBHOOK_SSL_CERT)
        db_api.insert.transactions(trans_id=int(data.split('_')[1]),status='done')
        tb.send_message(chat_id=query.message.chat.id, text='Забанены')

        return

    if 'cid-' in data:
        ch = db_api.get.channels(channel_name=data.split('-')[1])[0]
        pg = data.split('-')[2]

        if ch['mod'] == 1:

            mark = answ.gen_inl([[{'text': '◀️', 'data': 'pgnс_{}'.format(pg)}],
                                 [{'text': '❌ Удалить',
                                   'data': 'declinec-{}'.format(ch['channel_name'])}]])


        else:

            mark = answ.gen_inl([[{'text': '◀️', 'data': 'pgnс_{}'.format(pg)}],
                                 [{'text': '✅ Принять', 'data': 'acceptcid-{}'.format(ch['channel_name'])},
                                  {'text': '❌ Удалить',
                                   'data': 'declinec-{}'.format(ch['channel_name'])}]])

        text = '''Канал: [{}](https://t.me/{})
[Заказчик](tg://user?id={})
Просмотры {}:
СТоимость подписки: {}
'''.format(ch['channel_name'], ch['channel_name'].replace('@',''),ch['user_id'], ch['views'], ch['cost'])
        try:
            return tb.edit_message_text(text=text, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                    reply_markup=mark,parse_mode='Markdown')
        except:
            text = '''Канал: [{}](https://t.me/{})
Заказчик {}
Просмотры {}:
СТоимость подписки: {}
            '''.format(ch['channel_name'], ch['channel_name'].replace('@',''), ch['user_id'], ch['views'], ch['cost'])
            return tb.edit_message_text(text=text, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                    reply_markup=mark,parse_mode='Markdown')




    if 'tid' in data:
        tr = db_api.get.transactions(trans_id=int(data.split('_')[1]))[0]
        pg = data.split('_')[2]
        dup = db_api.get.transactions(qiwi_number=tr['qiwi_number'],type='pay_out')
        s = {}
        ban_button=[]
        for i in dup:
            s.update({str(i['user_id']):i['qiwi_number']})

        if len(s)>1:
            bans.update({str(tr['trans_id']):list(s.keys())})
            te = 'Есть дубликаты!: ' + ' '.join(s.keys())
            ban_button=[[{'text': '🚫 Ban', 'data': 'ban_{}'.format(tr['trans_id'])}]]
        else:
            te='Дубликатов нет!'
        if tr['menu'] == 'QIWI':
            number = helpers.check_number(tr['qiwi_number'])
            if number:
                db_api.insert.transactions(trans_id=tr['trans_id'],qiwi_number=number)
                mark = answ.gen_inl([[{'text':'◀️','data':'pgn_{}'.format(pg)}],[{'text':'✅ Принять','data':'acceptid_{}'.format(tr['trans_id'])},{'text':'⚠️ Автовывод','data':'autoidq_{}_{}'.format(tr['trans_id'],pg)},{'text':'❌ Отклонить','data':'decline_{}'.format(tr['trans_id'])}]]+ban_button)
            else:
                tb.send_message(chat_id=query.message.chat.id,text=tr['qiwi_number'])
                mark = answ.gen_inl([[{'text':'◀️','data':'pgn_{}'.format(pg)}],[{'text':'✅ Принять','data':'acceptid_{}'.format(tr['trans_id'])},{'text':'❗️ Автовывод','data':'err_{}'.format(tr['trans_id'])},{'text':'❌ Отклонить','data':'decline_{}'.format(tr['trans_id'])}]]+ban_button)
        elif tr['menu'] == 'YA':
            number = tr['qiwi_number']
            mark = answ.gen_inl([[{'text': '◀️', 'data': 'pgn_{}'.format(pg)}],
                                 [{'text': '✅ Принять', 'data': 'acceptid_{}'.format(tr['trans_id'])},
                                  {'text': '⚠️ Автовывод', 'data': 'autoidy_{}_{}'.format(tr['trans_id'], pg)},
                                  {'text': '❌ Отклонить', 'data': 'decline_{}'.format(tr['trans_id'])}]]+ban_button)

        else:
            number = tr['qiwi_number']
            mark = answ.gen_inl([[{'text':'◀️','data':'pgn_{}'.format(pg)}],[{'text':'✅ Принять','data':'acceptid_{}'.format(tr['trans_id'])},{'text':'❌ Отклонить','data':'decline_{}'.format(tr['trans_id'])}]]+ban_button)

        text = '''Пользователь: @{} 
id: {}
Номер {}: {}
Сумма для вывода: {}
Дата: {}
'''.format(tr['username'],tr['user_id'],tr['menu'],number,tr['count'],tr['date'])+te


        return tb.edit_message_text(text=text,chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=mark)

    if 'pgnс_' in data:
        return tb.edit_message_text(chat_id=query.message.chat.id,message_id=query.message.message_id,text='Меню вывода',reply_markup=answ.inline_channels(int(data.replace('pgnс_',''))))

    if 'pgn_' in data:
        return tb.edit_message_text(chat_id=query.message.chat.id,message_id=query.message.message_id,text='Меню вывода',reply_markup=answ.inline_requests(int(data.replace('pgn_',''))))



    if 'autoidq' in data:
        tr = db_api.get.transactions(trans_id=int(data.split('_')[1]))[0]
        number = helpers.check_number(tr['qiwi_number'])
        pg = data.split('_')[2]
        pay_result = qiwi.make_payment(round(tr['count'],2),number)
        if pay_result[0]:

            if pay_result[1]['transaction']['state']['code'] == 'Accepted':
                db_api.insert.transactions(trans_id=tr['trans_id'], status='done')

                return tb.edit_message_text(text='✅ успешно!', chat_id=query.message.chat.id, message_id=query.message.message_id,
                                            reply_markup=answ.gen_inl([[{'text':'◀️','data':'pgn_{}'.format(pg)}]]))
            else:
                return tb.edit_message_text(text='⚠️ {}'.format(pay_result[1]['transaction']['state']['code']), chat_id=query.message.chat.id, message_id=query.message.message_id,
                                            reply_markup=answ.gen_inl([[{'text':'◀️','data':'pgn_{}'.format(pg)}]]))
        else:
            return tb.edit_message_text(text='⛔️ {}'.format(pay_result[1]),
                                        chat_id=query.message.chat.id, message_id=query.message.message_id,
                                        reply_markup=answ.gen_inl([[{'text': '◀️', 'data': 'pgn_{}'.format(pg)}]]))

    if 'autoidy' in data:
        tr = db_api.get.transactions(trans_id=int(data.split('_')[1]))[0]
        pg = data.split('_')[2]
        pay_result = wallet.request_payment({'pattern_id':'p2p','to':tr['qiwi_number'],'amount':tr['count'],'comment':settings.out_comment,'message':settings.out_comment})
        if pay_result['status']=='success':
            pay_result = wallet.process_payment( {'request_id': pay_result['request_id']})
            if pay_result['status'] == 'success':
                db_api.insert.transactions(trans_id=tr['trans_id'], status='done')

                return tb.edit_message_text(text='✅ успешно!', chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            reply_markup=answ.gen_inl(
                                                [[{'text': '◀️', 'data': 'pgn_{}'.format(pg)}]]))
            else:
                return tb.edit_message_text(text='⚠️ {}'.format(pay_result['error_description']),
                                            chat_id=query.message.chat.id, message_id=query.message.message_id,
                                            reply_markup=answ.gen_inl(
                                                [[{'text': '◀️', 'data': 'pgn_{}'.format(pg)}]]))
        else:
            return tb.edit_message_text(text='⛔️ {}'.format(pay_result['error_description']),
                                        chat_id=query.message.chat.id, message_id=query.message.message_id,
                                        reply_markup=answ.gen_inl(
                                            [[{'text': '◀️', 'data': 'pgn_{}'.format(pg)}]]))


                    # except:
    #     return




# print(tb.remove_webhook())
# tb.polling(none_stop=True)

app = flask.Flask(__name__)
# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''



# Process webhook calls
@app.route(settings.WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        tb.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


print(tb.remove_webhook())
time.sleep(2)
# # Set webhook
s = settings.WEBHOOK_URL_BASE+settings.WEBHOOK_URL_PATH
print(s)
print(tb.set_webhook(url=settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH,
                certificate=open(settings.WEBHOOK_SSL_CERT, 'r'),allowed_updates=['update_id','message','edited_message','channel_post','edited_channel_post','inline_query','chosen_inline_result','callback_query','shipping_query','pre_checkout_query']))

app.run(host=settings.WEBHOOK_LISTEN,
        port=settings.WEBHOOK_PORT,
        ssl_context=(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV),threaded=True)
