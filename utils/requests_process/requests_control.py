#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/4/24 15:59
# @Author : 谈林海
import json
from functools import wraps

import httpx
from utils import *
from utils.commons.allure_control import ReportStyle
from utils.commons.singleton_control import singleton
from utils.data_process.json_control import JsonHandler
from utils.requests_process.create_cookie_control import Cookies

payload = {"account": config.account,
           "password": config.password
           }


@singleton
class Authentication:
    """获取token/cookies"""

    @staticmethod
    def cookie_token():
        try:
            res = httpx.post('https://tianqiai/login', data=payload)
            js = JsonHandler(res.json())
            res_cookies, res_token = res.cookies, js.find_one('$..token')
            return res_cookies, res_token
        except Exception as err:
            logger.warning(f'未获取到登录认证信息，请检查: {err}')
            return Cookies, {}  # 如果cookie没有获取成功，则根据全局配置域名生成一个备用cookie


@singleton
class RestClient:
    """
    基于 httpx 封装的同步请求类
    """

    def __init__(self):
        self.cookies, self.token = Authentication.cookie_token()
        self.client = httpx.Client(cookies=self.cookies, timeout=30, verify=False)

    def res_log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            url, method = args[1][:2]
            headers, data, json_data = kwargs.get('headers'), kwargs.get('data'), kwargs.get('json')
            response = res.text
            try:
                resp = json.loads(response)
            except json.decoder.JSONDecodeError:
                logger.info('请求返回结果为text类型')
                resp = res.status_code
            print("\n===============================================================")
            res_info = f"\n请求地址: {url}\n" \
                       f"请求方法: {method.upper()}\n" \
                       f"请求头: {headers}\n" \
                       f"请求数据: {data or json_data}\n" \
                       f"响应数据: {resp}\n" \
                       f"响应耗时(ms): {float(round(res.elapsed.total_seconds() * 1000))}\n" \
                       f"接口响应码: {res.status_code}\n"
            logger.info(res_info)
            ReportStyle.allure_step_no(f"请求地址: {url}")
            ReportStyle.allure_step_no(f"请求方法: {method.upper()}")
            ReportStyle.allure_step("请求头", headers)
            ReportStyle.allure_step("请求数据", data or json_data)
            ReportStyle.allure_step_no(f"接口响应码: {res.status_code}")
            ReportStyle.allure_step_no(f"响应耗时(ms): {round(res.elapsed.total_seconds() * 1000)}")
            ReportStyle.allure_step("响应数据", resp)
            return res.status_code if isinstance(resp, int) else res

        return wrapper

    @res_log
    def request(self, *args, **kwargs):
        try:
            url, request_method, _ = args[0]
        except ValueError:
            url, request_method = args[0]
        # 发起请求
        res = self.client.request(request_method, url, **kwargs)
        # 接口请求结果
        try:
            return res
        except Exception as err:
            logger.error(f'请求失败: {err}')
            return None

    @staticmethod
    def headers():
        """全局headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
            # 'token': self.token
        }
        return headers

    res_log = staticmethod(res_log)
