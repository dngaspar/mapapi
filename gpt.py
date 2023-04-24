import googlemaps
import pandas as pd

# Replace 'YOUR_API_KEY' with your actual API key
gmaps = googlemaps.Client(key="AIzaSyCiQyTQ8iblBIaILbDuzS0oURGcn2nGb0c")


def get_walking_time(org_location, num_places):
    """
    Get places within a 15-minute walking distance from the specified location,
    such as public transportation, major facilities, educational institutions, and hospitals.

    Parameters:
    org_location (str): A string representing the departure location, such as an address or place name.
    num_places (int): Number of places to retrieve per category.

    Returns:
    pandas.DataFrame: A dataframe containing the category, departure location, and walking time of the retrieved places.
    """
    # Get the latitude and longitude from the departure location.
    location = gmaps.geocode(org_location)
    assert location, "Location not found"
    region_location = location[0]["geometry"]["location"]
    org_latlng = f"{region_location['lat']}, {region_location['lng']}"

    # Set the mode to "walking" for using Google Maps Directions API.
    mode = "walking"

    # Set the maximum walking time to 15 minutes to retrieve places within a 15-minute walking distance.
    max_walking_time = 15 * 60  # 15 minutes to seconds conversion

    # Set the categories of the places to retrieve.
    queries = {
        "public_transport": "公共交通機関",
        "facilities": "主な施設",
        "education": "教育機関",
        "hospital": "病院",
    }

    # Initialize a dictionary to store the retrieved place information.
    result = {
        "category": [],
        "departure_location": [],
        "walking_time": [],
    }

    # Retrieve places for each category and store only the places within a 15-minute walking distance.
    for query_key, query_value in queries.items():
        # Retrieve all nearby places within a certain radius.
        places_result = gmaps.places_nearby(
            location=org_latlng, radius=5000, type=query_key
        )

        # Retrieve up to num_places places for this category.
        num_places_retrieved = 0
        for place in places_result["results"]:
            if num_places_retrieved == num_places:
                break

            # Only store places within a 15-minute walking distance.
            latlng = place["geometry"]["location"]
            walking_time_result = gmaps.distance_matrix(
                origins=org_latlng, destinations=latlng, mode=mode
            )
            walking_time = walking_time_result["rows"][0]["elements"][0]["duration"][
                "value"
            ]
            if walking_time <= max_walking_time:
                result["category"].append(query_value)
                result["departure_location"].append(place["name"])
                result["walking_time"].append(f"{walking_time // 60} minutes")
                num_places_retrieved += 1

    # Convert the result to a dataframe and return it.
    df = pd.DataFrame(result)
    return df


org = "静岡市葵区 西草深町 28-31"
resp_df = get_walking_time(org, 10)
resp_df.to_csv(f"{org}.csv", index=False)
print(resp_df)
