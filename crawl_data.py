#!/bin/python3

import datetime
import json
import requests

def crawl_data():
    current_date = datetime.datetime.now()
    month = ("0" + str(current_date.month)) if current_date.month < 10 else str(current_date.month)
    day = ("0" + str(current_date.day)) if current_date.day < 10 else str(current_date.day)
    date = month + '/' + day + '/' + str(current_date.year)
    url = 'https://tc-vaihingen-rohr.ebusy.de/lite-module/762?timestamp=&currentDate=' + date
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.get(url, headers=headers)
    with open("/home/pi/workspace/ebusy-crawler/data/bookingData.json", 'r') as out_file_json:
        json_data = out_file_json.read()
    data = json.loads(json_data)
    data.append(r.json())
    with open("/home/pi/workspace/ebusy-crawler/data/bookingData.json", 'w') as out_file_json:
        out_file_json.write(json.dumps(data))
    reservations = r.json().get("reservations")
    entry_sep = ","
    with open("/home/pi/workspace/ebusy-crawler/data/bookingData_" + date.replace("/", "_") + ".txt", 'w') as out_file:
        for reservation in reservations:
            out_file.write(str(reservation.get("id")) + entry_sep +
                           str(reservation.get("court")) + entry_sep +
                           str(reservation.get("booking")) + entry_sep +
                           reservation.get("date") + entry_sep +
                           reservation.get("fromTime") + entry_sep +
                           reservation.get("toTime") + entry_sep +
                           reservation.get("text") + entry_sep +
                           reservation.get("shortText") + entry_sep +
                           reservation.get("info") + entry_sep +
                           str(reservation.get("showDetailsLink")) + entry_sep +
                           str(reservation.get("blocking")) + entry_sep +
                           str(reservation.get("notComplete")) + entry_sep +
                           str(reservation.get("additionalPlayers")))
            out_file.write("\n")


if __name__ == '__main__':
    crawl_data()
