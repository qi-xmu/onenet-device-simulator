from model import *
import os

product = os.getenv("PRODUCT")  # 产品ID
name = os.getenv("NAME")  # 设备名称
skey = os.getenv("SKEY")  # 设备密钥

led1 = LedModel(name, product, skey)

led1.connect()
