"""
03.05.2025 | Maximilian
❤
"""

##################################################
#                    Imports                     #
##################################################

import requests
import json

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.factory import Factory
from kivy.clock import Clock


##################################################
#                     Code                       #
##################################################

kivy.require('2.0.0')


class AlarmItem:
    def __init__(self, time="00:00", active=True):
        self.time = time
        self.active = active

    def to_dict(self):
        return {"time": self.time, "active": self.active}


class MyLayout(Widget):
    pass


def sync_alarms_with_server(alarms):
    url = "http://10.0.0.69:6969/alarms"
    payload = {"alarms": [alarm.to_dict() for alarm in alarms]}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Alarm gespeichert!")
            return True
        else:
            print("Fehler:", response.json().get("error"), "Code:", response.status_code)
            return False
    except Exception as e:
        print("Verbindung fehlgeschlagen:", e)
        return False


def get_alarms_from_server():
    url = "http://10.0.0.69:6969/alarms"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("alarms", [])
        else:
            print("Fehler beim Abrufen der Wecker:", response.status_code)
            return None
    except Exception as e:
        print("Verbindung fehlgeschlagen:", e)
        return None


class KiddoVA(App):
    alarms = ListProperty([])

    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        # Load saved alarms if any
        self.load_alarms()

        # Check for server alarms every 5 seconds
        Clock.schedule_interval(self.check_server_alarms, 5)

        return MyLayout()

    def load_alarms(self):
        try:
            with open("alarms.json", "r") as f:
                saved_alarms = json.load(f)
                self.alarms = [AlarmItem(alarm["time"], alarm["active"]) for alarm in saved_alarms]
        except (FileNotFoundError, json.JSONDecodeError):
            # If no saved alarms, initialize with empty list
            self.alarms = []

    def check_server_alarms(self):
        server_alarms = get_alarms_from_server()
        if server_alarms is not None:
            # Check if the server alarms are different from local alarms
            updated = False
            if len(server_alarms) == len(self.alarms):
                for i, server_alarm in enumerate(server_alarms):
                    if (server_alarm.get("active") != self.alarms[i].active or
                        server_alarm.get("time") != self.alarms[i].time):
                        updated = True
                        break
            else:
                updated = True

            if updated:
                self.alarms = [AlarmItem(alarm["time"], alarm["active"]) for alarm in server_alarms]
                self.save_alarms_locally()
                Clock.schedule_once(lambda dt: self.update_alarm_widgets())

    def save_alarms_locally(self):
        with open("alarms.json", "w") as f:
            json.dump([alarm.to_dict() for alarm in self.alarms], f)

    def save_alarms(self):
        self.save_alarms_locally()
        sync_alarms_with_server(self.alarms)

    def set_alarm(self, time_text):
        if len(self.alarms) >= 3:
            # Limit reached, show error popup
            popup = Factory.MaxAlarmsReached()
            popup.open()
            return

        # Add new alarm
        new_alarm = AlarmItem(time_text, True)
        self.alarms.append(new_alarm)
        self.save_alarms()

        # Update UI
        Clock.schedule_once(lambda dt: self.update_alarm_widgets())

    def update_alarm_widgets(self,):
        alarm_container = self.root.ids.alarm_container
        alarm_container.clear_widgets()

        for i, alarm in enumerate(reversed(self.alarms)):
            alarm_widget = Factory.AlarmWidget()
            alarm_widget.alarm_time = alarm.time
            alarm_widget.active = alarm.active
            alarm_widget.index = len(self.alarms) - 1 - i
            alarm_container.add_widget(alarm_widget)

    def toggle_alarm(self, index, active):
        if 0 <= index < len(self.alarms):
            self.alarms[index].active = active
            self.save_alarms()

    def delete_alarm(self, index):
        if 0 <= index < len(self.alarms):
            self.alarms.pop(index)
            self.save_alarms()
            # If list is empty, file is deleted/overwritten with empty list
            if not self.alarms:
                self.clear_alarm_file()
            Clock.schedule_once(lambda dt: self.update_alarm_widgets())

    @staticmethod
    def clear_alarm_file():
        try:
            # Write an empty list to the file
            with open("alarms.json", "w") as f:
                json.dump([], f)

            # Send an empty list to the server
            requests.post("http://10.0.0.69:6969/alarms", json={"alarms": []})
            print("Alle Alarme wurden gelöscht")
        except Exception as e:
            print(f"Fehler beim Löschen der Alarmdatei: {e}")


if __name__ == '__main__':
    KiddoVA().run()