import sys
import os

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# for path in (SCRIPT_DIR, PROJECT_ROOT):
#     if path not in sys.path:
#         sys.path.insert(0, path)

sys.path.append("..")
from utilities.utils import generate_utc_time, generate_uuid, calculate_distance


import random
riders = ['rider_1001', 'rider_1002', 'rider_1003', 'rider_1004', 'rider_1005']


def create_ride_requested(ride):

    ride_requested_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "ride_requested",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "service_type": ride["service_type"],
        "city": ride["city"],
        "pickup": ride["pickup"],
        "dropoff": ride["dropoff"],
        "distance": ride["distance"],
        "duration": ride["duration"],
        "fare": ride["fare"]
    }

    return ride_requested_event

def create_driver_assigned(ride, driver):

    driver_assigned_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "driver_assigned",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "driver_id": ride["driver_id"],
        "service_type": ride["service_type"],
        "city": ride["city"],
        "pickup": ride["pickup"],
        "driver_distance_km": calculate_distance(driver["latitude"],
                                                 driver["longitude"],
                                                 ride["pickup"]["latitude"],
                                                 ride["pickup"]["longitude"]),
        "estimated_arrival_minutes": random.randint(5, 10),
        "distance": ride["distance"],
        "duration": ride["duration"],
        "fare": ride["fare"]
    }

    return driver_assigned_event

def create_ride_started(ride):

    ride_started_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "ride_started",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "driver_id": ride["driver_id"],
        "service_type": ride["service_type"],
        "city": ride["city"],
        "distance": ride["distance"],
        "duration": ride["duration"],
        "fare": ride["fare"]

    }

    return ride_started_event

def create_ride_completed(ride):


    ride_completed_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "ride_completed",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "driver_id": ride["driver_id"],
        "service_type": ride["service_type"],
        "city": ride["city"],
        "distance": ride["distance"],
        "duration": ride["duration"],
        "fare": ride["fare"]
    }

    return ride_completed_event


def create_cancel_ride(ride):

    driver_cancellation_reason = ["Rider not responding", "Undesired Destination", "Incorrect Pickup Location"]
    rider_cancellation_reason = ["Changed my mind", "Driver taking too long", "Found another ride", "Price too high"]

    if ride["driver_id"]:    
        cancelled_by  = random.choice(["driver", "rider"])
    else:
        cancelled_by = "rider"

    if cancelled_by == "driver":
        cancellation_reason = random.choice(driver_cancellation_reason)
    else:
        cancellation_reason = random.choice(rider_cancellation_reason)


    cancel_ride_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "ride_cancelled",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "driver_id": ride["driver_id"],
        "service_type": ride["service_type"],
        "city": ride["city"],
        "distance": ride["distance"],
        "duration": ride["duration"],
        "fare": ride["fare"],
        "cancelled_by": cancelled_by,
        "cancellation_reason": cancellation_reason
    }

    return cancel_ride_event

def create_payment_event(ride):

    payment_method = random.choice(["CASH", "UPI", "CARD"])

    payment_event = {
        "event_id": generate_uuid("evt"),
        "event_type": "payment_event",
        "event_timestamp": generate_utc_time(),
        "ride_id": ride["ride_id"],
        "rider_id": ride["rider_id"],
        "driver_id": ride["driver_id"],
        "city": ride["city"],
        "distance": ride["distance"],
        "duration": ride["duration"],
        "amount": ride["fare"],
        "currency": "INR",
        "payment_method": payment_method,
        "payment_status": "Paid"

    }
    return payment_event


def initialise_rider():

    riders_state = {}
    for rider_id in riders:
        rider_state = {
            "rider_id": rider_id,
            "status": "available",
            "last_updated_at": generate_utc_time()
        }
        riders_state[rider_id]=rider_state

    return riders_state



def get_available_rider(riders_state):

    available_riders = [rider["rider_id"] for rider in riders_state.values() if rider["status"]=="available"]

    if available_riders:
        return random.choice(available_riders)

    return None
    


# riders_state = initialise_rider()
# print(riders_state)
# print("\n")
# rider = get_available_rider(riders_state)
# print(rider)
# if __name__ == "__main__":

#     ride_id = generate_uuid("ride")

#     rider_id = random.choice(riders)
#     driver_id = random.choice(drivers)
#     service_type = random.choice(service_types)
#     city = random.choice(cities)

#     event1 = generate_ride_requested(ride_id, rider_id, service_type, city)

#     event2 = generate_driver_assigned(ride_id, rider_id, driver_id, city)

#     event3 = generate_ride_started(ride_id, rider_id, driver_id, city)

#     event4 = generate_ride_completed(ride_id, rider_id, driver_id, city)

#     events = [event1, event2, event3, event4]

#     for event in events:
#         print(event)
#     with open("Events.txt", "w") as file:
#         for event in events:
#             file.write(f"{event}\n\n")

