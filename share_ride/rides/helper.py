from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from accounts.models import Profile
from rides.models import Ride
from geopy.distance import geodesic  # For distance calculation
geolocator = Nominatim(user_agent="ride-tracking")

def convert_geocode_to_location(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else None
    except Exception:
        return None

def convert_location_to_geocode(location):
    """
    Convert a location string to latitude and longitude.
    Returns a tuple (latitude, longitude) or None if conversion fails.
    """
    try:
        # Geocode the location string
        geocode_result = geolocator.geocode(location, timeout=10)
        if geocode_result:
            return (geocode_result.latitude, geocode_result.longitude)
        return None
    except (GeocoderTimedOut, GeocoderUnavailable, Exception) as e:
        print(f"Error geocoding {location}: {str(e)}")
        return None

def find_available_driver(ride):
    """
    Returns the closest available driver to the ride's pickup location.
    """
    drivers = Profile.objects.filter(user_type="driver")
    if not drivers.exists():
        return None

    # Geocode ride's pickup location 
    try:
        pickup_coords = convert_location_to_geocode(ride.pickup_location)
    except Exception:
        return None  # Fallback if geocoding fails

    closest_driver = None
    min_distance = float('inf')

    for driver in drivers:
        # Check if driver is free
        engaged = Ride.objects.filter(driver=driver, status__in=["requested", "accepted", "started"]).exists()
        if engaged:
            continue

        # Assume Profile has current_latitude/current_longitude
        if not (driver.current_latitude and driver.current_longitude):
            continue  # Skip drivers without location

        driver_coords = (driver.current_latitude, driver.current_longitude)
        distance = geodesic(pickup_coords, driver_coords).kilometers

        if distance < min_distance:
            min_distance = distance
            closest_driver = driver

    return closest_driver