import sys
import os
sys.path.append(os.path.abspath(".."))

import random, time
import json
from ride_simulator import create_driver_assigned, create_ride_requested, create_ride_started, create_ride_completed
from utilities.utils import generate_utc_time, generate_uuid, seconds_in_current_state, print_json

riders = ['rider_1001', 'rider_1002', 'rider_1003', 'rider_1004', 'rider_1005']
drivers = ['driver_2001', 'driver_2002', 'driver_2003', 'driver_2004', 'driver_2005']
cities = ['Bangalore', 'Mumbai', 'Pune', 'Hyderabad', 'Delhi']
service_types = ['UberX', 'UberXL', 'UberGo', 'Premier']
active_rides={}
STATE_DURATIONS = {
    "requested": random.randint(5,10),
    "assigned": random.randint(10,20),
    "started":random.randint(15,25),
}


def create_new_ride():

    ride_id = generate_uuid("ride")

    rider_id = random.choice(riders)
    service_type = random.choice(service_types)
    city = random.choice(cities)

    ride = {
        "ride_id": ride_id,
        "rider_id": rider_id,
        "driver_id": None,
        "city": city,
        "service_type": service_type,
        "status": "requested",
        "last_state_change": time.time(),
        "required_state_duration":STATE_DURATIONS.get("requested")
    }
    #adding to dict active_rides with ride_id as the key
    active_rides[ride_id]= ride

    return ride

def generate_requested_event(ride:dict):

    return create_ride_requested(ride["ride_id"], ride["rider_id"], ride["service_type"], ride["city"])

def assign_driver(ride):

    ride["driver_id"] = random.choice(drivers)
    ride["status"] = "assigned"
    ride["last_state_change"] = time.time()
    ride["required_state_duration"] = STATE_DURATIONS.get("assigned")

    return create_driver_assigned(ride["ride_id"], 
                                 ride["rider_id"], 
                                 ride["driver_id"], 
                                 ride["city"])

def start_ride(ride):

    ride["status"] = "started"
    ride["last_state_change"] = time.time()
    ride["required_state_duration"] = STATE_DURATIONS.get("started")

    return create_ride_started(ride["ride_id"], 
                                 ride["rider_id"], 
                                 ride["driver_id"], 
                                 ride["city"])

def complete_ride(ride):

    ride["status"] = "completed"
    ride["last_state_change"] = time.time()

    return create_ride_completed(ride["ride_id"], 
                                 ride["rider_id"], 
                                 ride["driver_id"], 
                                 ride["city"])


def advance_ride(ride:dict):

  
    status = ride["status"]

    # completed
    #     ↓
    # nothing
    if status == "completed":
        return None

    #elapsed_time = diff btw current time and last state change time
    elapsed_time = seconds_in_current_state(ride)
    #required_time = time required for changing from one status to another status
    # required_time = STATE_DURATIONS.get(status)
    required_time = ride["required_state_duration"]

    if elapsed_time < required_time:
        return None

    # requested
    #     ↓
    # assign_driver()
    if status == "requested":
        event = assign_driver(ride)
        return event

    # assigned
    #     ↓
    # start_ride()    
    if status == "assigned":
        event = start_ride(ride)
        return event
    
    # started
    #     ↓
    # complete_ride()
    if status == "started":
        event = complete_ride(ride)
        return event
 


while True:

    print("running")

    existing_rides = list(active_rides.values())

    with open("Event_Gen_Random.txt", "a") as file:
    #create new ride -> generate requested event -> driver assigned -> started -> completed
        new_ride = create_new_ride()

        #generate requested event
        event = generate_requested_event(new_ride)
        

        # file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n{json.dumps(event,indent=4)}\n\n")
        file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n\n")

        #for each ride in active_rides -> advancing the ride 
        for ride  in existing_rides:
            event = advance_ride(ride)

            if event:
                # file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n{json.dumps(event,indent=4)}\n\n")
                file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n\n")

    time.sleep(5)
                





# if __name__ == "__main__":

#     with open ("Events.txt", "w")as file:

#         ride = create_new_ride()
#         file.write(f"BEFORE \n {json.dumps(ride, indent=4)}")

#         event = generate_requested_event(ride)
#         file.write(f"\nEVENTS:\n{json.dumps(event, indent=4)}")

#         event = assign_driver(ride)
#         file.write(f"\nAfter Driver assignment \n{json.dumps(ride, indent=4)} \n\nEVENT \n {json.dumps(event, indent=4)}")

#         event = start_ride(ride)
#         file.write(f"\nRIDE STARTED\n {json.dumps(ride, indent=4)}\nEVENT: \n{json.dumps(event, indent=4)}")

#         event = complete_ride(ride)
#         file.write(f"\nRIDE COMPLETED\n {json.dumps(ride, indent=4)}\n EVENT:\n {json.dumps(event, indent=4)}")


