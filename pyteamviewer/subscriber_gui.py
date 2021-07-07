import subscriber

mqtt_subscriber = subscriber.Subscriber(
        "raspberrypi",
        1883,
        1,
        {
            "top": 150,
            "left": 100,
            "width": 700,
            "height": 300
        }
)
mqtt_subscriber.connect()
