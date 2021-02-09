from math import *
import geocoder

# Geocoder is not very accuarate....
def find_me():
    """
    This is a function that takes no arguments and returns your machine's current lat/lon coordinates.
    This will help find the closet Raspberry Pi weather station to you.
    """
    return geocoder.ip('me').latlng

def haversine_to_me(lat, lon):
    """
    This function takes a coordinate and calculates the distance between your machine and the given location,
    using the Haversine formula. This is calculated in kilometers.
    """

    lat1 = radians(38.924507)
    lon1 = radians(-77.081216)
    lat2 = radians(lat)
    lon2 = radians(lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1


    a = pow(sin(dlat/2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon/2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return c * 6371

# Dalecarlia Reservoir
print("Haversine distance to Dalecarlia (km):", haversine_to_me(38.9425, -77.1100))

# National Arboretum
print("Haversine distance to Arboretum (km):",haversine_to_me(38.9121, -76.9658))

# Reagan Airport
print("Haversine distance to Reagan (km):",haversine_to_me(38.8512, -77.0402))
