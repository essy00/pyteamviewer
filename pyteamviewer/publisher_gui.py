import os

from PIL import Image, ImageTk
import tkinter as tk

import publisher


class PublisherGUI:
    """
        The GUI of the controlled screen.
    """
    def __init__(self):
        """
        Initializing the class.
        """
        self.root = tk.Tk()
        self.screen_widget = ImageTk.PhotoImage(
            image=Image.open("black.png")
        )
        self.panel = tk.Label(self.root, image=self.screen_widget)
        self.panel.pack(side="bottom", fill="both", expand="yes")

    def screen_data(self):
        """
        Tries to read the temporary file to show on the screen.
        """
        try:
            self.screen_widget = ImageTk.PhotoImage(
                image=Image.open("tmp.jpg")
            )
            self.panel.configure(image=self.screen_widget)
            self.panel.image = self.screen_widget

        except Exception:
            pass

        finally:
            self.root.after(1, self.screen_data)


    def run(self):
        """
        Starts the GUI
        """
        self.screen_data()
        self.root.mainloop()


mqtt_publisher = publisher.Publisher("raspberrypi", 1883, 1, (300, 700))
mqtt_publisher.connect()

gui = PublisherGUI()
gui.run()

mqtt_publisher.connected = False
os.remove("tmp.jpg")
