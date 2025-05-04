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
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window


##################################################
#                     Code                       #
##################################################

kivy.require('2.0.0')
Builder.load_file("kiddova.kv")

class MyLayout(Widget):
    pass


class KiddoVA(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return MyLayout()

if __name__ == '__main__':
    KiddoVA().run()


