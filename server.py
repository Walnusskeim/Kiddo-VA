import os
import time
import threading
import json
from datetime import datetime, timedelta

from flask import Flask, request


app = Flask(__name__)
active_alarms = {}  # Dictionary to store active alarm threads


def wait_for_alarm(alarm_id, alarm_time_str):
    print(f"Wecker {alarm_id} gesetzt fuer: {alarm_time_str}")
    
    alarm_time = datetime.strptime(alarm_time_str, "%H:%M")
    now = datetime.now()
    alarm_time_today = now.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)

    if alarm_time_today < now:
        alarm_time_today += timedelta(days=1)

    total_time = (alarm_time_today - now).total_seconds()
    print(f"Warte {total_time} Sekunden für Wecker {alarm_id}...")
    time.sleep(total_time)

    # If time is reached
    print(f"Weckerzeit erreicht für Wecker {alarm_id}!")
    if alarm_id in active_alarms:
        del active_alarms[alarm_id]


@app.route('/alarm', methods=['POST'])
def receive_single_alarm():
    """Legacy endpoint for backward compatibility"""
    data = request.json
    alarm_time = data.get('time')

    if not alarm_time:
        return {"error": "Keine Uhrzeit gesendet!"}, 400

    # Create a single alarm
    alarm_id = "single_alarm"
    
    # Cancel any existing alarm thread
    if alarm_id in active_alarms and active_alarms[alarm_id].is_alive():
        # Cannot directly stop thread, but we can remove it from active_alarms
        del active_alarms[alarm_id]
        
    # Start new alarm thread
    alarm_thread = threading.Thread(target=wait_for_alarm, args=(alarm_id, alarm_time), daemon=True)
    alarm_thread.start()
    active_alarms[alarm_id] = alarm_thread

    return {"time": alarm_time}, 200


@app.route('/alarms', methods=['POST'])
def receive_alarms():
    data = request.json
    alarms_data = data.get('alarms', [])

    if not alarms_data:
        return {"error": "Keine Wecker gesendet!"}, 400

    # Save alarms to file
    with open("alarms.json", "w") as f:
        json.dump(alarms_data, f)

    # Clear all existing alarm threads
    active_alarms.clear()

    # Start threads for active alarms
    for i, alarm in enumerate(alarms_data):
        if alarm.get('active', False):
            alarm_id = f"alarm_{i}"
            alarm_time = alarm.get('time')
            alarm_thread = threading.Thread(target=wait_for_alarm, args=(alarm_id, alarm_time), daemon=True)
            alarm_thread.start()
            active_alarms[alarm_id] = alarm_thread

    return {"status": "Wecker gespeichert", "count": len(alarms_data)}, 200


@app.route('/alarms', methods=['GET'])
def get_alarms():
    try:
        with open("alarms.json", "r") as f:
            alarms = json.load(f)
        return {"alarms": alarms}, 200
    except (FileNotFoundError, json.JSONDecodeError):
        return {"alarms": []}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
