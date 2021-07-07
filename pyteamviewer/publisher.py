from pynput import keyboard, mouse
import paho.mqtt.client as mqtt
import numpy as np
import cv2
import threading
import enum


class Publisher:
    def __init__(self, broker: str, port: int, connection_id: int, screen_size: tuple) -> None:
        """
        Initializing the class.

        Args:
            broker (str): The MQTT broker.
            port (int): The port.
            connection_id (int): The connection ID.
            screen_size (tuple): The screen size, like (300, 700):
        """
        self.broker = broker
        self.port = port
        self.connection_id = connection_id
        self.screen_size = (*screen_size, 4)

        self.client = mqtt.Client()
        self.base_connection = "connection_" + str(connection_id)

        self.screen = None

        self.mouse_timing = {
                "tick": 0,
                "delay": 20
        }
        self.scroll_timing = {
                "tick": 0,
                "delay": 20
        }

        self.connected = True

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
            print('Error:', str(rc))
            self.connected = False

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        """
        MQTT's on_message function.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata ([type]): The private user data as set in Client() or user_data_set().
            msg (mqtt.MQTTMessage): An instance of MQTTMessage. This is a class with members topic, payload, qos, retain.
        """
        if msg.topic.split("/")[-1] == "screen":
            self.screen = np.frombuffer(msg.payload, dtype="uint8").reshape(self.screen_size)

    def on_press(self, key: keyboard.Key) -> None:
        """
        Detects when a key is pressed.

        Args:
            key (pynput.keyboard.Key): Pressed key.
        """
        self.client.publish(self.base_connection + "/keyboard", str(key))

    def on_release(self, key: keyboard.Key) -> None:
        """
        Detects when a key is released.

        Args:
            key (pynput.keyboard.Key): Released key.
        """
        # TODO set the hotkeys
        pass

    def on_move(self, x: int, y: int) -> None:
        """
        Detects when the mouse is moved.

        Args:
            x (int): X axis.
            y (int): Y axis.
        """
        self.mouse_timing["tick"] += 1

        if self.mouse_timing["tick"] >= self.mouse_timing["delay"]:
            self.mouse_timing["tick"] = 0
            self.client.publish(self.base_connection + "/mouse", f"moved-{x}-{y}")

    def on_click(self, x: int, y: int, button: enum, pressed: bool) -> None:
        """
        Detects when it's clicked.

        Args:
            x (int): X axis.
            y (int): Y axis.
            button (enum): Button type.
            pressed (bool): True if pressed, False if released.
        """
        data = ""

        if button == mouse.Button.right:
            data = "pressed-right" if pressed else "released-right"

        elif button == mouse.Button.left:
            data = "pressed-left" if pressed else "released-left"

        elif button == mouse.Button.middle:
            data = "pressed-middle" if pressed else "released-middle"

        self.client.publish(self.base_connection + "/mouse", data)

    def on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Detects when it's scrolled.

        Args:
            x (int): X axis
            y (int): Y axis
            dx (int): The horizontal offset.
            dy (int): The vertical offset.
        """
        self.scroll_timing["tick"] += 1
        
        if self.scroll_timing["tick"] >= self.scroll_timing["delay"]:
            self.scroll_timing["tick"] = 0
            self.client.publish(
                    self.base_connection + "/mouse",
                    "scrolled-down" if dy < 0 else "scrolled-up"
            )

    def connect(self) -> None:
        """
        Connects the publisher with the subscriber.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.connect(self.broker, self.port)
        self.client.subscribe(self.base_connection + "/screen")

        self.client.loop_start()
        
        keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        keyboard_listener.start()
	
        mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        mouse_listener.start()

        t = threading.Thread(target=self.update_screen)
        t.start()

    def update_screen(self) -> None:
        """
        Updates the screen.
        """
        while self.connected:
            if self.screen is not None:
                cv2.imwrite("tmp.jpg", self.screen)
