import json
import paho.mqtt.client as mqtt
from utils import *


class LedModel:
    def __init__(self, name, product, skey):
        self.properties = {
            "BrightValue": 10,  # int32 亮度值
            "TempValue": 0,  # int32 冷暖值
            "SwitchLed": False,  # bool 灯的开关
            "SwitchPir": False,  # bool 感应的开关
        }
        self.msg_id = 0

        #
        self.name = name
        self.product = product
        self.skey = skey
        self.client = ""

        self.topics = {
            f"$sys/{product}/{name}/thing/property/post/reply": self._on_property_post_reply,
            f"$sys/{product}/{name}/thing/property/set": self._on_property_set,
            f"$sys/{product}/{name}/thing/property/get": self._on_property_get,
        }

    def connect(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.get_client_id(),
            clean_session=True,
        )
        username, password = self.get_user()
        self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        # self.client.on_disconnect = self._on_connect

        self.client.connect("mqtts.heclouds.com", 1883, 60)
        self.client.loop_forever()

    def send(self, topic, params):
        print(f"< Send: {params}")
        self.client.publish(topic, json.dumps(params))
        # see now properties
        self.data_consumer()

    def _on_message(self, client, userdata, msg):
        params = json.loads(msg.payload.decode("utf-8"))
        self.on_recv(params)
        self.topics[msg.topic](params)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")

        if reason_code == "Success":
            print("Subscribe...")
            for topic in self.topics.keys():
                client.subscribe(topic)

    def get_client_id(self):
        return self.name

    def get_user(self):
        token = get_token(self.product, self.skey)
        return self.product, token

    def _on_property_post_reply(self, params):
        """
            数据上报响应
        :param params:{
        "id": "123",
        "code":200,
        "msg":"xxxx"
        }
        """
        print(params)
        self.data_consumer()

    def _on_property_set(self, params):
        # $sys/{pid}/{device-name}/thing/property/set_reply
        reply_topic = f"$sys/{self.product}/{self.name}/thing/property/set_reply"
        reply = {
            "id": params["id"],
            "code": 200,
            "msg": "",
        }
        # print(params)

        for key, value in params["params"].items():
            if key in self.properties:
                self.properties[key] = value
            else:
                print(f"key: {key} not in properties")

        self.send(reply_topic, reply)

    def on_recv(self, params):
        print(f"> Recv: {params}")

    def _on_property_get(self, params):
        # $sys/{pid}/{device-name}/thing/property/get_reply
        reply_topic = f"$sys/{self.product}/{self.name}/thing/property/get_reply"
        reply = {
            "id": params["id"],
            "code": 200,
            "msg": "",
            "data": {},
        }

        for key in params["params"]:
            if key in self.properties:
                reply["data"][key] = self.properties[key]
            else:
                print(f"key: {key} not in properties")

        self.send(reply_topic, reply)

    def data_consumer(self):
        # 使用绿色字体输入
        print(f"\033[32m{self.properties}\033[0m")
        pass
