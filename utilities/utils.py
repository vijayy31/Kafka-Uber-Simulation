def generate_uuid(prefix:str):

    import uuid

    id = str(uuid.uuid4())
    uid=f"{prefix}_{id[24:]}"

    return uid


def generate_utc_time():

    from datetime import datetime, timezone

    utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return utc_time


def print_json(event:dict):

    for key, value in event.items():
        print(f"{key}: {value}")

def seconds_in_current_state(ride):
    import time

    return time.time()-ride["last_state_change"]

city_coordinates = {
    "Bangalore": {
        "latitude": (12.90, 13.05),
        "longitude": (77.50, 77.70)
    },
    "Mumbai": {
        "latitude": (18.90, 19.20),
        "longitude": (72.75, 73.05)
    },
    "Pune": {
        "latitude": (18.45, 18.65),
        "longitude": (73.75, 73.95)
    },
    "Hyderabad": {
        "latitude": (17.30, 17.55),
        "longitude": (78.30, 78.60)
    },
    "Delhi": {
        "latitude": (28.50, 28.80),
        "longitude": (76.90, 77.35)
    }
}


def generate_location_coordinates(city):
    import random

    coord = city_coordinates[city]

    latitude = round(random.uniform(coord["latitude"][0], coord["latitude"][1]),6)
    longitude = round(random.uniform(coord["longitude"][0], coord["longitude"][1]),6)

    return {
        "latitude": latitude,
        "longitude": longitude
    }

def generate_unique_coordinates(pickup, city):

    dropoff = generate_location_coordinates(city)

    while True:
        if pickup["latitude"] == dropoff["latitude"] and pickup["longitude"] == dropoff["longitude"]:
            dropoff = generate_location_coordinates(city)
        else:
            break

    return dropoff

#copied from gpt
def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c, 2)


if __name__ == "__main__":

    # uid = generate_uuid("evt")
    # utc = generate_utc_time()
    # print(uid, utc)

    pickup = generate_location_coordinates("Delhi")
    dropoff = generate_unique_coordinates(pickup, "Delhi")

    print(pickup, dropoff)