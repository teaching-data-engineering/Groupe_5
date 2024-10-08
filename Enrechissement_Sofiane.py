from geopy.geocoders import Nominatim
import random

def adress_to_coords(adresse):
    location = geolocator.geocode(adresse)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


for adresse in df.lieu:
    geolocator = Nominatim(user_agent=f"mon_geocode{random.randint(10000, 100000)}")
    latitude, longitude = adress_to_coords(adresse)
    df.loc[df['lieu'] == adresse, ['latitude', 'longitude']] = [latitude, longitude]
