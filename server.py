import os
import time
import threading
from datetime import datetime, timedelta

from flask import Flask, request


app = Flask(__name__)


def wait(alarm_time_str):
    print(f"Wecker gesetzt fuer: {alarm_time_str}")
    with open("alarm.txt", "w") as f:
        f.write(alarm_time_str)
        f.close()

    alarm_time = datetime.strptime(alarm_time_str, "%H:%M")

    now = datetime.now()
    alarm_time_today = now.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)

    if alarm_time_today < now:
        alarm_time_today += timedelta(days=1)

    total_time = (alarm_time_today - now).total_seconds()
    print(f"Warte {total_time} Sekunden...")
    time.sleep(total_time)

    # If time is reached
    print("Weckerzeit erreicht!")
    os.remove("alarm.txt")


@app.route('/alarm', methods=['POST'])
def receive():
    data = request.json
    alarm_time = data.get('time')

    if not alarm_time:
        return {"error": "Keine Uhrzeit gesendet!"}, 400

    # Thread to wait for the alarm time
    threading.Thread(target=wait, args=(alarm_time,), daemon=True).start()

    return {"time": alarm_time}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)