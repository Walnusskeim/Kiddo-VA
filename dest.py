import requests

def send(time: str):
    url = "http://<RASPI_IP>:6969/alarm"
    payload = {"time": time}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Es klingelt um:", response.json().get("time"))

        else:
            print("Fehler:", response.json().get("error"), "Code:", response.status_code)

    except Exception as e:
        print("Verbindung fehlgeschlagen:", e)


if __name__ == "__main__":
    time = input("Gib eine Uhrzeit im Format HH:MM ein: ")
    send(time)