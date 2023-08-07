#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict, Union

from utils import root
from utils.fake_data.fake_data_control import Mock
from utils.read_file_process.read_yaml_control import HandleYaml


class Config(BaseModel):
    """定义配置类"""

    cache_path: Union[str, Path] = root / 'test_data/cache.yaml'


class DataHandler:
    def __init__(self, config: Config):
        self.config = config
        self.cache_data = self.load_cache()

    def load_cache(self) -> Dict[str, Any]:
        """加载缓存数据"""

        cache_path = Path(self.config.cache_path)
        return HandleYaml(cache_path).read_yaml().get('cache', {})

    def replace_values(self, data):
        """ 替换字典中指定格式的字符串值 """

        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self._replace_value(value)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                data[index] = self._replace_value(item)
        return data

    def _replace_value(self, value):
        """替换指定格式的字符串值"""

        if isinstance(value, (dict, list)):
            return self.replace_values(value)
        elif isinstance(value, str):
            return self._replace_str_value(value)
        else:
            return value

    def _replace_str_value(self, value):
        """替换字符串中的特定格式"""

        if '{{' in value and '}}' in value and 'int.' not in value and 'str.' not in value:
            func = value[value.find('{') + 2:value.find('}')]
            return value.replace('{{%s}}' % func, str(Mock(func)()))
        elif '$cache.' in value:
            cache_name = value[value.find('.') + 1:]
            return self.cache_data.get(cache_name, None)
        elif 'int.' in value:
            func = value[value.find('{') + 2:value.find('}')]
            return int(value.replace('{{%s}}' % func, str(Mock(func[func.find('.') + 1:])())))
        elif 'str.' in value:
            func = value[value.find('{') + 2:value.find('}')]
            return str(value.replace('{{%s}}' % func, str(Mock(func[func.find('.') + 1:])())))
        else:
            return value

