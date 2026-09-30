import sys
import os
sys.path.append("..")

from utilities.utils import generate_utc_time, generate_uuid, generate_location_coordinates, calculate_distance

import random, time
import json

drivers = ['driver_2001', 'driver_2002', 'driver_2003', 'driver_2004', 'driver_2005']
cities = ['Bangalore', 'Mumbai', 'Pune', 'Hyderabad', 'Delhi']

def initialize_drivers():
    drivers_state={}
    for driver_id in drivers:

        city = random.choice(cities)
        location_coord = generate_location_coordinates(city)
        
        driver_state = {
            "driver_id": driver_id,
            "city": city,
            "latitude": round(location_coord["latitude"],6),
            "longitude": location_coord["longitude"],
            "speed_kmh": 0,
            "status": "available",
            "current_ride_id": None

        }

        drivers_state[driver_id]=driver_state

    return drivers_state
        

def create_driver_location_event(driver):

    driver_loc_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "driver_location",
        "event_timestamp": generate_utc_time(),
        "driver_id": driver["driver_id"],
        "ride_id": driver["current_ride_id"],
        "city": driver["city"],
        "latitude": driver["latitude"],
        "longitude": driver["longitude"],
        "speed_kmh": driver["speed_kmh"],
        "status": driver["status"]
    }

    return driver_loc_event

def move_driver(driver, active_rides):

    driver_status = driver["status"]

    ride = None
    ride_id = driver["current_ride_id"]

    if ride_id:
        ride = active_rides[ride_id]

    if driver_status == "offline":
        driver["speed_kmh"] = 0
        return
    
    if driver_status == "available":

        driver["latitude"] += random.uniform(-0.001, 0.001)
        driver["longitude"] += random.uniform(-0.001, 0.001)

        driver["speed_kmh"] = round(random.uniform(0, 30), 2)

    elif driver_status == "en_route":

        calculate_driver_location(driver, ride["pickup"])

        driver["speed_kmh"] = round(random.uniform(10, 50), 2)

        
    elif driver_status == "on_trip":
    
        calculate_driver_location(driver, ride["dropoff"])

        driver["speed_kmh"] = round(random.uniform(10, 50), 2)

    driver["latitude"] = round(driver["latitude"],6)
    driver["longitude"] = round(driver["longitude"],6)


def calculate_driver_location(driver, destined_location):

    destination = destined_location
    
    move_towards(
                driver,
                destination["latitude"],
                destination["longitude"]
            )
    
    has_reached = has_reached_check(driver, destination)

    if has_reached:
        driver["latitude"] = destination["latitude"]
        driver["longitude"] = destination["longitude"]


    driver["latitude"] = round(driver["latitude"],6)
    driver["longitude"] = round(driver["longitude"],6)

    # return has_reached

def has_reached_check(driver, destined_location):

    destination = destined_location
    distance = calculate_distance(driver["latitude"], driver["longitude"], destination["latitude"],destination["longitude"])
    # print(distance)
    has_reached = distance < 0.1
    # print(has_reached)
    if has_reached:
        return True
    else:
        return False
     

def move_towards(driver, target_latitude, target_longitude):

    step = 0.005

    lat_difference = target_latitude - driver["latitude"]
    lon_difference = target_longitude - driver["longitude"]

    if abs(lat_difference) < step:
        driver["latitude"] = target_latitude
    else:
        driver["latitude"] += step if lat_difference > 0 else -step

    if abs(lon_difference) < step:
        driver["longitude"] = target_longitude
    else:
        driver["longitude"] += step if lon_difference > 0 else -step



def get_available_driver(drivers_state, city):

    available_drivers = [driver for driver in drivers_state.values() if driver["status"]=="available" and driver["city"]==city]

    if not available_drivers:
        return None

    return random.choice(available_drivers)


