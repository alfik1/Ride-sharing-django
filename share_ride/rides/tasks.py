from celery import shared_task
from .models import Ride
from .helper import convert_geocode_to_location
import random
import time

@shared_task
def simulate_ride_tracking(ride_id):
    """
    Simulate real-time tracking by updating the ride's location with mock coordinates.
    """
    try:
        ride = Ride.objects.get(id=ride_id)
        if ride.status not in ["started"]:  # Only simulate for active rides
            return f"Simulation stopped: Ride {ride_id} is not in 'started' status."

        # GET initital coordinates 
        current_lat = ride.current_latitude
        current_lon = ride.current_longitude 

        # Simulate movement 
        for _ in range(5):
            # Small random movement (e.g., 0.01 degrees ~ 1.1 km)
            current_lat += random.uniform(-0.01, 0.01)
            current_lon += random.uniform(-0.01, 0.01)

            # Ensure coordinates are within valid ranges
            current_lat = max(min(current_lat, 90), -90)
            current_lon = max(min(current_lon, 180), -180)

            # Update ride location
            location = convert_geocode_to_location(current_lat, current_lon)
            ride.current_location = location
            ride.current_latitude = current_lat
            ride.current_longitude = current_lon
            ride.save()

            # Simulate time delay between updates (e.g., 10 seconds)
            time.sleep(10)  # Adjust interval as needed

        # Optionally mark ride as completed after simulation
        ride.status = "completed"
        ride.save()
        return f"Simulation completed for ride {ride_id}."

    except Ride.DoesNotExist:
        return f"Ride {ride_id} not found."
    except Exception as e:
        return f"Error during simulation for ride {ride_id}: {str(e)}"