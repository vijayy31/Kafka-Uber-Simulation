ride_simulator.py.

It will:

1. Generate a rider.
2. Create a ride_id.
3. Generate ride_requested.
4. Assign a driver.
5. Generate driver_assigned.
6. Generate ride_started.
7. Generate either ride_completed or ride_cancelled.
8. If completed, generate payment_completed.
9. Publish each event to Kafka with ride_id as the message key.