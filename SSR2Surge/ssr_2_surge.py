#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/28
# @Author  : silence
# @File    : SSR2Surge.py
# @Project : SSR2Surge

import urllib.request
from ssr_parser import *

# SSR订阅地址
ssr_config_url = ''
# ss-local路径
exec_path = 'ss-local'
# 本地端口
local_port_start = 1025


def get_ssr_config():
    config_response = urllib.request.urlopen(ssr_config_url)
    base64_config = config_response.read().decode()
    config_scheme = base64_decode(base64_config)
    config_list = config_scheme.split()

    ssr_list = []

    index = 0
    for ssr_scheme in config_list:
        ssr_config = parse_ssr_url(ssr_scheme)

        ssr_config['local_port'] = str(local_port_start + index)
        ssr_config['exec_path'] = exec_path
        # print(ssr_config)
        index += 1
        if ssr_config['obfs'] == 'http_simple' :
            continue
        surge_config = ssr_2_surge(ssr_config)
        ssr_list.append(surge_config)
    return ssr_list


def ssr_2_surge(ssr_config):
    surge_config = ssr_config['name'] + ' ='
    surge_config += ' external, exec = "%(exec_path)s",' % ssr_config
    surge_config += ' local-port = %(local_port)s,' % ssr_config
    surge_config += ' args = "-o", args = "%(obfs)s",' % ssr_config
    surge_config += ' args = "-O", args = "%(protocol)s",' % ssr_config
    surge_config += ' args = "-G", args = "%(protoparam)s",' % ssr_config
    surge_config += ' args = "-s", args = "%(server)s",' % ssr_config
    surge_config += ' args = "-p", args = "%(server_port)s",' % ssr_config
    surge_config += ' args = "-l", args = "%(local_port)s",' % ssr_config
    surge_config += ' args = "-b", args = "127.0.0.1",'
    surge_config += ' args = "-k", args = "%(password)s",' % ssr_config
    surge_config += ' args = "-m", args = "%(method)s",' % ssr_config
    surge_config += ' addresses = "%(server)s"\n' % ssr_config

    return surge_config


if __name__ == '__main__':
    surge_list = get_ssr_config()

    with open('surge.conf','w+') as f:
        f.writelines(surge_list)
