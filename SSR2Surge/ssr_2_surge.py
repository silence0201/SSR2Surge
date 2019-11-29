#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/28
# @Author  : silence
# @File    : SSR2Surge.py
# @Project : SSR2Surge

import urllib.request as request
from ssr_parser import *

# SSR订阅地址,支持多地址配置
ssr_config_url = [
    '',
    '']
# ss-local路径
exec_path = 'ss-local'
# 本地端口
local_port_start = 1025


def get_proxy_config(config_url):
    headers = {'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}
    url = request.Request(config_url, headers=headers)
    config_response = request.urlopen(url)
    base64_config = config_response.read().decode()
    config_scheme = base64_decode(base64_config)
    config_list = config_scheme.split()

    ssr_list = []
    proxy_group = {}

    index = 0
    for ssr_scheme in config_list:
        ssr_config = parse_ssr_url(ssr_scheme)
        if ssr_config is None:
            continue

        ssr_config['local_port'] = str(local_port_start + index)
        ssr_config['exec_path'] = exec_path

        group = ssr_config['group']
        proxy_name = ssr_config['name']
        if group not in proxy_group:
            proxy_group[group] = []
        proxy_group[group].append(proxy_name)

        if is_ss(ssr_config):
            surge_config = ss_2_surge(ssr_config)
        else:
            surge_config = ssr_2_surge(ssr_config)
            index += 1

        ssr_list.append(surge_config)

    return ssr_list, proxy_group


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


def ss_2_surge(ss_config):
    surge_config = ss_config['name'] + ' ='
    surge_config += ' ss, %(server)s, %(server_port)s, encrypt-method=%(method)s, password=%(password)s, tfo=true \n' % ss_config
    return surge_config


def is_ss(config):
    return config['obfs'] == 'http_simple'


def proxy_list(name, proxys):
    proxy_config = name + ' = select'
    for proxy in proxys:
        proxy_config += ', ' + proxy
    return proxy_config


if __name__ == '__main__':
    surge_list = []
    proxy_group = {}

    for config_url in ssr_config_url:
        list, group = get_proxy_config(config_url)
        surge_list.extend(list)
        proxy_group.update(group)

    with open('surge.list', 'w+') as f:
        f.write('[Proxy]\n')
        f.writelines(surge_list)
        f.write('[Proxy Group]\n')

        for name, proxys in proxy_group.items():
            proxy_str = ', '.join(proxys)
            proxy_list = name + ' = select, ' + proxy_str + '\n'
            f.write(proxy_list)
