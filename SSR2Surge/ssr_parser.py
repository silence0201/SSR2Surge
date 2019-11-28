#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/28
# @Author  : silence
# @File    : ssr_parser.py
# @Project : SSR2Surge

import base64
import re


def fill_padding(base64_encode_str):
   need_padding = len(base64_encode_str) % 4 != 0

   if need_padding:
       missing_padding = 4 - need_padding
       base64_encode_str += '=' * missing_padding
   return base64_encode_str


def base64_decode(base64_encode_str):
   base64_encode_str = fill_padding(base64_encode_str)
   return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')


def parse_ssr_url(ssr_url: str):
    result = {}

    _, url_body = ssr_url.split('://')
    url_body = base64_decode(url_body)

    config = re.split(':', url_body)

    ip = config[0]
    port = config[1]
    protocol = config[2]
    method = config[3]
    obfs = config[4]

    password_and_params = config[5]
    password_and_params = password_and_params.split("/?")

    password_encode_str = password_and_params[0]
    password = base64_decode(password_encode_str)
    params = password_and_params[1]

    param_parts = params.split('&')

    param_dic = {}
    for part in param_parts:
        key_and_value = part.split('=')
        param_dic[key_and_value[0]] = key_and_value[1]

    obfsparam = base64_decode(param_dic['obfsparam'])
    protoparam = base64_decode(param_dic['protoparam'])
    remarks = base64_decode(param_dic['remarks'])
    group = base64_decode(param_dic['group'])

    result.update({'server': ip,
                   'method': method,
                   'obfs': obfs,
                   'password': password,
                   'server_port': port,
                   'protocol': protocol,
                   'obfsparam' : obfsparam,
                   'protoparam' : protoparam,
                   'name' : remarks,
                   'group' : group
                   })
    return result

