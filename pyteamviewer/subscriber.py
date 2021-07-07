from itertools import count
import platform

from mss import mss
import paho.mqtt.client as mqtt
import numpy as np
import pyautogui
import pyperclip


def type_utf_8(key: str):
    """
    A function to type UTF-8.

    Args:
        key (str): The letter.
    """
    pyperclip.copy(key)
    if platform.system() == "Darwin":
        pyautogui.hotkey("command", "v")
    else:
        pyautogui.hotkey("ctrl", "v")


class Subscriber:
    def __init__(self, broker: str, port: int, connection_id: int, screen_size: dict):
        """
        Initializing the class.

        Args:
            broker (str): The MQTT broker.
            port (int): The port.
            connection_id (int): The connection ID.
            screen_size (dict): The screen size, which is a dictionary,
                which should be like: 
                    {"top": 40, "left": 0, "width": 800, "height": 640}
        """
        self.broker = broker
        self.port = port
        self.connection_id = connection_id
        self.base_connection = "connection_" + str(self.connection_id)
        self.screen_size = screen_size
        self.client = mqtt.Client()
        self.sct = mss()

    def on_connect(self, client: mqtt.Client, userdata: None, flags: dict, rc: int) -> None:
        """
        MQTT's on_connect function.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata ([type]): The private user data as set in Client() or user_data_set().
            flags (dict): Flags is a dict that contains response flags from the broker.
            rc (int): The connection result.
        """
        if rc == 0:
            print("Connected.")
        else:
            print("Error:", str(rc))

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        """
        MQTT's on_message function.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata ([type]): The private user data as set in Client() or user_data_set().
            msg (mqtt.MQTTMessage): An instance of MQTTMessage. This is a class with members topic, payload, qos, retain.
        """
        message = msg.payload.decode("utf-8")
        topic = msg.topic

        if topic.split("/")[-1] == "keyboard":
            print(message)
            key = message.replace("'", "")

            if key == ".":
                type_utf_8(".")

            key = key.split(".")
            if len(key) > 1:
                pyautogui.press(key[1])

            else:
                type_utf_8(key[0])

        elif topic.split("/")[-1] == "mouse":
            args = message.split("-")

            if args[0] == "moved":
                pyautogui.moveTo(int(args[1]), int(args[2]))

            elif args[0] == "pressed":
                pyautogui.mouseDown(button=args[1])

            elif args[0] == "released":
                pyautogui.mouseUp(button=args[1])

            elif args[0] == "scrolled":
                if args[1] == "down":
                    pyautogui.scroll(-5)

                elif args[1] == "up":
                    pyautogui.scroll(5)

    def connect(self) -> None:
        """
        Connects the subscriber with the publisher.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port)
        self.client.subscribe(self.base_connection + "/keyboard")
        self.client.subscribe(self.base_connection + "/mouse")

        self.client.loop_start()

        for i in count(0):
            if i % 2000000 == 0:
                sct_img = self.sct.grab(self.screen_size)
                self.client.publish(
                        self.base_connection + "/screen",
                        np.array(sct_img).tobytes()
                )
