"""
03.05.2025 | Maximilian
❤
"""

##################################################
#                    Imports                     #
##################################################

import time
import requests

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window


##################################################
#                     Code                       #
##################################################

kivy.require('2.0.0')


class MyLayout(Widget):
    pass



def set_alarm(time):
    url = "http://10.0.0.69:6969/alarm"
    payload = {"time": time}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Es klingelt um:", response.json().get("time"))
        else:
            print("Fehler:", response.json().get("error"), "Code:", response.status_code)
    except Exception as e:
        print("Verbindung fehlgeschlagen:", e)


class KiddoVA(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return MyLayout()


if __name__ == '__main__':
    KiddoVA().run()
