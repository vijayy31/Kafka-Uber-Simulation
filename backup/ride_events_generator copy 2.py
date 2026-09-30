import sys
import os

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# for path in (SCRIPT_DIR, PROJECT_ROOT):
#     if path not in sys.path:
#         sys.path.insert(0, path)

import random, time
import json
from ride_simulator import create_driver_assigned, create_ride_requested, create_ride_started, create_ride_completed, create_cancel_ride, create_payment_event
from utilities.utils import generate_utc_time, generate_uuid, seconds_in_current_state, print_json, generate_location_coordinates, generate_unique_coordinates

riders = ['rider_1001', 'rider_1002', 'rider_1003', 'rider_1004', 'rider_1005']
drivers = ['driver_2001', 'driver_2002', 'driver_2003', 'driver_2004', 'driver_2005']
cities = ['Bangalore', 'Mumbai', 'Pune', 'Hyderabad', 'Delhi']
service_types = ['UberX', 'UberXL', 'UberGo', 'Premier']
active_rides={}
STATE_DURATIONS = {
    "requested": random.randint(5,20),
    "assigned": random.randint(15,25),
    "started":random.randint(15,25),
    "completed": 2
}
last_ride_created = {
    "last_created_time":None,
    "required_time_to_create_new_ride":None
}



def create_new_ride():

    last_ride_creation_time = last_ride_created["last_created_time"]
    required_new_ride_creation_time = last_ride_created["required_time_to_create_new_ride"]

    if last_ride_creation_time:

        if time.time()-last_ride_creation_time < required_new_ride_creation_time:
            return None

    ride_id = generate_uuid("ride")

    rider_id = random.choice(riders)
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
        "required_state_duration":STATE_DURATIONS.get("requested")
    }
    #adding to dict active_rides with ride_id as the key
    active_rides[ride_id]= ride
    
    last_ride_created["last_created_time"] = time.time()
    last_ride_created["required_time_to_create_new_ride"]= random.randint(5,15)

    return ride

def generate_requested_event(ride:dict):

    return create_ride_requested(ride)

def assign_driver(ride):

    ride["driver_id"] = random.choice(drivers)
    ride["status"] = "assigned"
    

    return create_driver_assigned(ride)

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

def advance_ride(ride:dict):

  
    status = ride["status"]

    if status in ["requested", "assigned"]:

        if random.random()< 0.10: 
            #below 10% for cancellation
            event = cancel_ride(ride)
            return event
        
    # completed
    #     ↓
    # nothing
    if status in ["paid_complete", "cancelled"] :
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

    # assigned
    #     ↓
    # start_ride()    
    if status == "assigned":
        event = start_ride(ride)
    
    # started
    #     ↓
    # complete_ride()
    if status == "started":
        event = complete_ride(ride)

    # completed
    #     ↓
    # payment
    if status == "completed":
        event = payment_event(ride)

    ride["last_state_change"] = time.time()
    ride["required_state_duration"] = STATE_DURATIONS.get(status)

    return event
 

if __name__ == "__main__":
    while True:

        print("running")

        existing_rides = list(active_rides.values())

        with open("Event_Gen_Random-2.txt", "a") as file:
        #create new ride -> generate requested event -> driver assigned -> started -> completed
            new_ride = create_new_ride()

            if new_ride:
                #generate requested event
                event = generate_requested_event(new_ride)

                file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n{json.dumps(event,indent=4)}\n\n")
                # file.write(f'{event["event_type"].upper()}-{event["ride_id"]}\n\n')

            #for each ride in active_rides -> advancing the ride 
            for ride  in existing_rides:
                event = advance_ride(ride)

                if event:
                    file.write(f"{event["event_type"].upper()}-{event["ride_id"]}\n{json.dumps(event,indent=4)}\n\n")
                    # file.write(f'{event["event_type"].upper()}-{event["ride_id"]}\n\n')

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


