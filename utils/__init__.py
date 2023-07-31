#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import loguru
from pathlib import Path
from utils.commons.singleton_control import singleton
from utils.models.models import Config
from utils.read_file_process.read_yaml_control import HandleYaml

root = Path(__file__).resolve().parents[1]


@singleton
class Loggings:
    """日志操作方法"""

    log_path = '../logs'

    def __new__(cls, *args, **kwargs):
        loggers = loguru.logger
        loggers.add(f"{cls.log_path}/log_{time.strftime('%Y_%m_%d')}.log", rotation='1 day', encoding="utf-8",
                    enqueue=True, retention="10 days")
        return loggers


logger = Loggings()

config_data = HandleYaml(root / 'config.yml').read_yaml()
config = Config(**config_data)