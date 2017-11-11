db_url='sqlite:///../join_bot/db.sqlite'

ref_pay_perc_1lvl=0.15 #столько получит от 1 уровная рефералов за оплату
ref_pay_perc_2lvl=0 #столько получит от 2 уровная рефералов за оплату
ref_view_pay_1lvl=0.10 #столько получит от 1 уровная рефералов за подписку
ref_view_pay_2lvl=0.02 #столько получит от 2 уровная рефералов за подписку
user_view_perc=0.40 #столько получит пользователь за вступление(проценты от стоимости установленной заказчиком)
min_out_pay=10 #минимальная сумма для вывода
min_post_cost=0.6 #минимальная стоимость 1 подписчика

number=79083463109
qiwi_token = 'f2c251337b3c7780c0fbf74a6d7b2d1e'

ya_number=410014368136464
ya_token='410014368136464.BE6FB1E33AB880962458E34EBD6B5FC4D2B95473412F0CB906DD98755B714CBC3359863F04985EFE9A87E2FC7B2E09162CA60F1143557D342D5242C3F7E8CD0DB7933732D9A5C1F1351AEB405683319432A3F87F52FB4C3D28227A3CDDBEDCD3FDCFC860742C696892BC2D4CD89BF45FF85D9D60749BA8FDEA69133C9F6AFD5C'

telegram_token='391544383:AAFeXwobH1QIfjEWw-uYpI-m_kAOQDL9p7o'


uah_to_rub=2.16
usd_to_rub=57.85
eur_to_rub=67.73

admins = [6968547,357536678,469213095,337967992,393154628]


tutorial_url = 'http://telegra.ph/Kak-sdelat-bota-administratorom-10-14'

out_comment = "@EzCashRobot"



WEBHOOK_HOST = '35.196.88.73'
WEBHOOK_PORT = 88
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)

WEBHOOK_URL_PATH = "/{}/".format(telegram_token)
