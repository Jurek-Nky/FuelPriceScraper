# coding=utf-8
import datetime
import sqlite3
import time
import sys
from geopy.geocoders import Nominatim

import requests as req

try:
    from types import SimpleNamespace as Namespace
except ImportError:
    # Python 2.x fallback
    from argparse import Namespace


class ApiScraper:
    def __init__(self, postcode):
        self.db = sqlite3.connect("priceScraper.db")
        self.cur = self.db.cursor()
        self.geo_app = Nominatim(user_agent="fuelScraper")
        self.fetch_stations_in_radius(postcode)

    def fetch_stations_in_radius(self, postcode):
        location = self.geo_app.geocode("germany,{pc}".format(pc=postcode)).raw
        lat = location["lat"]
        lng = location["lon"]
        uri = "https://creativecommons.tankerkoenig.de/json/list.php?lat={lat}&lng={lng}&rad=25&sort=dist&type=all&apikey=c5ab76e0-a31e-ff0b-ea98-73d516446a35" \
            .format(lng=lng, lat=lat)
        response = req.get(uri)
        for station in response.json()["stations"]:
            pl = PriceList(station["e5"], station["e10"], station["diesel"])
            station_dto = GasStation(station["name"], station["id"], station["brand"],
                                     station["street"], station["houseNumber"], station["postCode"],
                                     station["place"], station["lat"], station["lng"])
            self.insert_into_db(station_dto, pl)

    def insert_into_db(self, station, prices):
        for row in self.cur.execute("select count(gs_id) from gasstations where gs_id = '{stations_id}'".format(
                stations_id=station.station_id)):
            # if station does not already exist it will be created
            if row[0] == 0:
                self.cur.execute(
                    "insert into gasstations (gs_id, name, brand, street, housenumber, postcode, place, lat, "
                    "lng) values (?,?,?,?,?,?,?,?,?)",
                    (station.station_id, station.name, station.brand, station.street, station.houseNumber,
                     station.postCode, station.place, station.lat, station.lng))
                print ("inserted new station with id {id}".format(id=station.station_id))
            # price list gets inserted with foreign key of the gasstation it belongs to
            self.cur.execute("INSERT INTO prices (gasstation,e5,e10,diesel,time_stamp) VALUES (?,?,?,?,?)",
                             (station.station_id, prices.e5, prices.e10, prices.diesel, prices.time_stamp))
            print ("inserted new price-list for station with id {id}".format(id=station.station_id))
        self.db.commit()


class GasStation:
    def __init__(self, name, station_id, brand, street, house_number, post_code, place, lat, lng):
        self.name, self.station_id, self.brand, self.street, self.houseNumber, self.postCode, self.place, self.lat, self.lng = name, station_id, brand, street, house_number, post_code, place, lat, lng
        self.price_history = []

    def new_price_list(self, e5, e10, diesel):
        price_list = PriceList(e5, e10, diesel)
        self.price_history.append(price_list)


class PriceList:
    def __init__(self, e5, e10, diesel):
        self.e5, self.e10, self.diesel = e5, e10, diesel
        self.time_stamp = datetime.datetime.now()


if __name__ == '__main__':
    while True:
        for code in sys.argv[1:]:
            ApiScraper(code)
        time.sleep(300)
