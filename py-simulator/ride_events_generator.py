import sys
import os

"""Generate ride lifecycle events and maintain the active-ride simulation loop.

This file creates new rides, assigns drivers, advances each ride through its
states, and writes events to output files as the simulation runs.
"""

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# for path in (SCRIPT_DIR, PROJECT_ROOT):
#     if path not in sys.path:
#         sys.path.insert(0, path)
sys.path.append("..")

import random, time
import json
from ride_simulator import create_driver_assigned, create_ride_requested, create_ride_started, create_ride_completed, create_cancel_ride, create_payment_event, initialise_rider, get_available_rider
from utilities.utils import generate_utc_time, generate_uuid, seconds_in_current_state, print_json, generate_location_coordinates, generate_unique_coordinates
from driver_simulator import get_available_driver, move_driver, initialize_drivers, calculate_driver_location, create_driver_location_event, has_reached_check

# riders = ['rider_1001', 'rider_1002', 'rider_1003', 'rider_1004', 'rider_1005']
# drivers = ['driver_2001', 'driver_2002', 'driver_2003', 'driver_2004', 'driver_2005']
# cities = ['Bangalore', 'Mumbai', 'Pune', 'Hyderabad', 'Delhi']


service_types = ['UberX', 'UberXL', 'UberGo', 'Premier']
# Store all rides currently active in the simulation.
active_rides={}

STATE_DURATIONS = {
    "requested": 0,
    "assigned": 0,
    "started":0,
    "completed": 2
}
last_ride_created = {
    "last_created_time":None,
    "required_time_to_create_new_ride":None,
}

DRIVER_LOCATION_EVENT_CREATION_INTERVAL = 5
last_driver_location_event_created = 0

drivers_state= initialize_drivers()
cities = [ driver["city"] for driver in drivers_state.values()]


removing_expired_rides = {
    "removing_interval": 20,
    "last_time_removed": time.time()
}

riders_state= initialise_rider()


# Create a new ride request only when the required cooldown has elapsed.
def create_new_ride():

    last_ride_creation_time = last_ride_created["last_created_time"]
    required_new_ride_creation_time = last_ride_created["required_time_to_create_new_ride"]

    if last_ride_creation_time:

        if time.time()-last_ride_creation_time < required_new_ride_creation_time:

            return None

    rider_id = get_available_rider(riders_state)
    if not rider_id:
        return None

    rider = riders_state[rider_id]
    rider["status"] = "on_trip"
    rider["last_updated_at"]= generate_utc_time()

    ride_id = generate_uuid("ride")

    service_type = random.choice(service_types)
    city = random.choice(cities)

    pickup = generate_location_coordinates(city)
    dropoff = generate_unique_coordinates(pickup, city)

    distance = round(random.uniform(2.0, 20.0), 2)
    duration = random.randint(10, 60)

    fare = round(50 + (distance*10) + (duration*2), 2)
    
    ride = {
        "ride_id": ride_id,
        "rider_id": rider_id,
        "driver_id": None,
        "city": city,
        "service_type": service_type,
        "status": "requested",
        "distance": distance,
        "duration": duration,
        "fare": fare,
        "pickup": pickup,
        "dropoff": dropoff,
        "last_state_change": time.time(),
        "required_state_duration":random.randint(10,20)
    }
    #adding to dict active_rides with ride_id as the key
    active_rides[ride_id]= ride
    
    last_ride_created["last_created_time"] = time.time()
    last_ride_created["required_time_to_create_new_ride"]= random.randint(1,5)

    return ride

# Emit the request event for a ride that has just been created.
def generate_requested_event(ride:dict):

    return create_ride_requested(ride)

# Assign a driver from the same city when a requested ride becomes eligible.
def assign_driver(ride):
    
    driver = get_available_driver(drivers_state, ride["city"])

    if driver is None:
        return None


    ride["driver_id"]= driver["driver_id"]
    ride["status"] = "assigned"

    driver["status"] = "en_route"
    driver["current_ride_id"] = ride["ride_id"]
    
    return create_driver_assigned(ride, driver)

def start_ride(ride):

    ride["status"] = "started"
    

    return create_ride_started(ride)

def complete_ride(ride):

    ride["status"] = "completed"
    

    return create_ride_completed(ride)

def payment_event(ride):

    ride["status"] = "paid_complete"
    ride["last_state_change"] = time.time()
    ride["required_state_duration"]= None
    
    return create_payment_event(ride)


def cancel_ride(ride):

    ride["status"] = "cancelled"
    ride["last_state_change"] = time.time()
    ride["required_state_duration"]= None


    return create_cancel_ride(ride)

# Advance the ride state machine based on elapsed time and destination checks.
def advance_ride(ride:dict):

    status = ride["status"]
    # print(status)
    if status in ["requested", "assigned"]:

        if random.random()< 0.005:  # 0.5% chance of cancellation
            
            if status == "assigned":
                cancelled_driver = drivers_state[ride["driver_id"]]
                cancelled_driver["status"]="available"
                cancelled_driver["current_ride_id"]=None

            rider = riders_state[ride["rider_id"]]
            rider["status"] = "available"
            rider["last_updated_at"]= generate_utc_time()

            event = cancel_ride(ride)

            return event
        
    # completed  -> nothing
    if status in ["paid_complete", "cancelled"] :
        return None

    #elapsed_time = diff btw current time and last state change time
    elapsed_time = seconds_in_current_state(ride)

    #required_time = time required for changing from one status to another status    
    required_time = ride["required_state_duration"]

    if elapsed_time < required_time:
        return None
    
    # requested -> assign_driver()
    if status == "requested":
        
        event = assign_driver(ride)
        
        if not event:
            return None

    # assigned -> start_ride()
        
    elif status == "assigned":
        
        assgn_driver = drivers_state[ride["driver_id"]]
        has_reached_pickup = has_reached_check(assgn_driver, ride["pickup"])

        
        if has_reached_pickup:

            event = start_ride(ride)

            assgn_driver["status"]="on_trip"

        else:
            return None

    
    # started -> complete_ride()
    elif status == "started":
        started_driver = drivers_state[ride["driver_id"]]
        has_reached_dropoff = has_reached_check(started_driver, ride["dropoff"])

        
        if has_reached_dropoff:
            
            event = complete_ride(ride)

            started_driver["status"]="available"
            started_driver["current_ride_id"]=None

        else:
            return None

    # completed
    #     ↓
    # payment
    elif status == "completed":
        event = payment_event(ride)

        rider = riders_state[ride["rider_id"]]

        rider["status"] = "available"
        rider["last_updated_at"]= generate_utc_time()

    
    ride["last_state_change"] = time.time()
    ride["required_state_duration"] = random.randint(10,20)

    return event


# Main simulation loop: update drivers, generate rides, and emit events.
if __name__ == "__main__":

    while True:

        print("running")
        with open("final_drive_event.txt", "a") as file2:

            for driver in drivers_state.values():
                move_driver(driver, active_rides)
                
                if time.time() - last_driver_location_event_created > DRIVER_LOCATION_EVENT_CREATION_INTERVAL:
                    # print(driver)
                    driver_event = create_driver_location_event(driver)
                    file2.write(f"{driver_event["event_type"].upper()}-{driver_event["driver_id"]}\n{json.dumps(driver_event,indent=4)}\n\n")

            if time.time() - last_driver_location_event_created > DRIVER_LOCATION_EVENT_CREATION_INTERVAL: 
                last_driver_location_event_created = time.time()

        with open("final_ride_event.txt", "a") as file1:

            existing_rides = list(active_rides.values())

            new_ride = create_new_ride()

            if new_ride:

                request_event = generate_requested_event(new_ride)
                file1.write(f"{request_event["event_type"].upper()}-{request_event["ride_id"]}\n{json.dumps(request_event,indent=4)}\n\n")
        
            for ride in existing_rides:

                next_event = advance_ride(ride)

                if next_event:
                    
                    file1.write(f"{next_event["event_type"].upper()}-{next_event["ride_id"]}\n{json.dumps(next_event,indent=4)}\n\n")

            
        if time.time() - removing_expired_rides["last_time_removed"] > removing_expired_rides["removing_interval"]:

            for expired_rides in list(active_rides.values()):

                status = expired_rides["status"]

                if status == "paid_complete":
                    ride_removed = active_rides.pop(expired_rides["ride_id"])

            removing_expired_rides["last_time_removed"]= time.time()

        time.sleep(1)

#removing the old rides from active rides - doone
#using only the available rider without duplicating it - done
#need to check the driver event change 