#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/4/3 17:55
# @Author : 谈林海
import allure
import pytest


@allure.feature('天气模块')
@allure.title('天气查询接口')
@pytest.mark.datafile('test_data/tianqi/test_tianqi.yml')
def test_tianqi(core, env, case, inputs, expectation):
    # core.requests: 返回请求方法对象
    # core.headers: 返回全局请求头
    # core.sql: 返回查询方法
    # core.cache: 返回缓存处理方法对象
    res = core.requests.request(env, data=inputs['json'], headers=core.headers).json()
    assert res['success'] == expectation['response']


