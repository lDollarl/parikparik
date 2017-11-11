#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import settings
import json
import time
url = "https://edge.qiwi.com/payment-history/v1/persons/{}/payments".format(settings.number)

querystring = {"rows":"50","operation":"IN"}


def get_history(**kwargs):
    headers = {
        'accept': "application/json",
        'authorization': "Bearer {}".format(settings.qiwi_token),
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers, params=kwargs)
    if response.status_code == 200:

        return json.loads(response.text)
    else:
        return False

def make_payment(amount,account):
    print(int(time.time()*1000))
    data = {
        "id":str(int(time.time()*1000)),
        "sum": {
          "amount":amount,
          "currency":"643"
        },
        "paymentMethod": {
          "type":"Account",
          "accountId":"643"
        },
        "comment":settings.out_comment,
        "fields": {
          "account":account
        }
      }
    headers = {
        'accept': "application/json",
        'authorization': "Bearer {}".format(settings.qiwi_token),
        'cache-control': "no-cache",
        'content-type': 'application/json'
    }



    response = requests.request("POST", 'https://edge.qiwi.com/sinap/api/v2/terms/99/payments', headers=headers, data=json.dumps(data))

    if response.status_code == 200:

        return True,json.loads(response.text)
    else:
        return False,json.loads(response.text)['message']


