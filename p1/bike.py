import argparse
import collections
import csv
import json
import glob
import math
import os
import pandas
import re
import requests
import string
import sys
import time
import xml
from requests import get


class Bike():
    baseURL = "https://api.nextbike.net/maps/gbfs/v1/nextbike_pp/en,"
    station_infoURL = ""
    station_statusURL = ""

    def __init__(self, baseURL, station_info, station_status):
        # initialize the instance
        self.baseURL = baseURL
        self.station_infoURL = baseURL + station_info
        self.station_statusURL = baseURL + station_status

    def total_bikes(self):
        # return the total number of bikes available
        num_bikes = 0
        response = get(self.station_statusURL, verify = False)
        status = json.loads(response.content)

        bikes = status['data']['stations']

        data_file = open('status.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in bikes:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()

        with open('status.csv', 'r') as csv_file:
            row_num = 0
            csv_reader = csv.reader(csv_file, delimiter = ",")
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    num_bikes += int(row[1])
        return num_bikes



    def total_docks(self):
        # return the total number of docks available
        num_docks = 0
        with open('status.csv', 'r') as csv_file:
            row_num =0
            csv_reader = csv.reader(csv_file, delimiter = ",")
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    num_docks += int(row[2])
        return num_docks

    def percent_avail(self, station_id):
        num_docks = 0
        num_bikes = 0
        result = ""

        response = get(self.station_statusURL, verify = False)
        status = json.loads(response.content)

        avail = status['data']['stations']

        data_file = open('status.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in avail:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()



        with open('status.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            row_num = 0
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    int_row = int(row[0])
                    if int_row == station_id:
                        num_docks = int(row[2])
                        num_bikes = int(row[1])
                        percent_avail = (num_docks / (num_docks + num_bikes)) * 100
                        result = str(math.floor(percent_avail)) + "%"
        return result

    def closest_stations(self, latitude, longitude):
        # return the stations closest to the given coordinates
        result = {}
        distance_points = {}
        sorted_items = []
        response = get(self.station_infoURL, verify = False)
        info = json.loads(response.content)

        data = info['data']['stations']

        data_file = open('info.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in data:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()
        count = 0

        with open('info.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            row_num = 0
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    float_lat = float(row[3])
                    float_lon = float(row[4])
                    dist = self.distance( latitude, longitude,  float_lat, float_lon)
                    if len(distance_points ) < 3:
                        distance_points[dist] = int(row[0])
                    else:
                        if count == 0:
                            items = distance_points.items()
                            sorted_items = sorted(items, reverse = True)

                            count += 1
                        else:
                        #    print("SORTING ", sorted_items)
                            sorted_items  = sorted(sorted_items, reverse = True)
                            #print("SORTED: ", sorted_items)
                        for i in sorted_items:
                            #print("CHECKING ", dist)
                            if dist < i[0]:

                                sorted_items.remove(i)
                                sorted_items.append((dist,int(row[0])))
                                break
            #print(sorted_items)
            csv_file.seek(0)
            for i in sorted_items:
                id = i[1]
                name = ""
                row_num = 0
                for row in csv_reader:
                    if row_num == 0:
                        row_num += 1
                    elif id == int(row[0]):
                        name = row[1]
                csv_file.seek(0)
                result[str(id)] = name
        return result





    def closest_bike(self, latitude, longitude):
        # return the station with available bikes closest to the given coordinates
        response = get(self.station_infoURL, verify = False)
        info = json.loads(response.content)
        res = {}
        result = {}
        data = info['data']['stations']

        data_file = open('info.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in data:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()
        count = 0
        min_dist = 0
        with open('info.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            row_num = 0
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    float_lat = float(row[3])
                    float_lon = float(row[4])
                    dist = self.distance( latitude, longitude,  float_lat, float_lon)
                    if len(res) == 0:
                        res[dist] = int(row[0])
                        min_dist = dist

                    else:
                        if dist < min_dist:
                            #print(res, dist)
                            res.clear()
                            res[dist] = int(row[0])
                            min_dist = dist

            id = res[min_dist]
            csv_file.seek(0)
            name = ""
            row_num = 0
            id += 1
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                elif int(row[0]) == id:
                    name = str(row[1])
            result[str(id)] = name
            return result






    def station_bike_avail(self, latitude, longitude):
        # return the station id and available bikes that correspond to the station with the given coordinates
        result = {}
        response = get(self.station_infoURL, verify = False)
        info = json.loads(response.content)

        data = info['data']['stations']

        data_file = open('info.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in data:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()
        station_id = 0
        bikes_avil = 0
        with open('info.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            row_num = 0
            for row in csv_reader:
                if row_num == 0:
                    row_num += 1
                else:
                    float_lat = float(row[3])
                    float_lon = float(row[4])
                    if (float_lat == latitude) and (float_lon == longitude):
                        station_id = int(row[0])



        response = get(self.station_statusURL, verify = False)
        status = json.loads(response.content)

        bikes = status['data']['stations']

        data_file = open('status.csv', 'w')
        csv_writer = csv.writer(data_file)
        count = 0

        for line in bikes:
            if count == 0:
                header = line.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(line.values())
        data_file.close()
        if station_id > 0:
            with open('status.csv', 'r') as status_file:
                csv_reader = csv.reader(status_file)
                row_num = 0
                for row in csv_reader:
                    if row_num == 0:
                        row_num += 1
                    elif int(row[0]) == station_id:
                        bikes_avil = int(row[1])
                        result[str(station_id)] = bikes_avil

        return result





    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('https://api.nextbike.net/maps/gbfs/v1/nextbike_pp/en', '/station_information.json', '/station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.450595, -80.013204) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
