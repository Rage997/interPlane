'''
This module contains everthing that directly relies on the skyscanner API
'''

import requests
from config import *
import time
from RouteException import RouteNotFoundException


headers = {
        "X-RapidAPI-Key": rapidAPI_key,
        "useQueryString": 'false'
}

def __check_response(response: str):
    if response.find('You have exceeded the rate limit per minute for your plan') != -1:
        return False
    else:
        return True


def get_airports(city='Anywhere', country=None):
    """ Get a list of airports IDs in a city. Many cities have multiple airports.

    Args:
        city (str, optional): The city. Defaults to 'Anywhere'.
        country ([type], optional): the country where the city is. Some cities have the same name in different countries. Defaults to None.

    Returns:
        [array]: returns all the ID of the airports in the city
    """    
   

    endpoint = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/{}/{}/en-{}/".format(
                configcountry, configcurrency, configcountry)
    headers["X-RapidAPI-Host"] = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com" 
    params = {"query": city}

    response = requests.get(endpoint,
                            headers=headers,
                                params=params
                                )

    while not __check_response(response.text):
        print('You have exceeded the rate limit per minute for your plan, waiting 60 seconds.')
        # print(response.text)
        time.sleep(60)
        response = requests.get(endpoint,
                        headers=headers,
                            params=params
                            )
    
    response = response.json()
    
    # print(response)
    places = response['Places']
    # print(places)

    if not country: 
        country = places[0]['CountryName']

    # We get all the airports in a given city (we filter for country to ensure that they are correct)
    airports = [city for city in places if city['CountryName'] == country]

    # Some airports have multiple identifiers, to prevent returning the same arport multiple times
    # we remove elments with the same PlaceID
    airports_unique = {each['PlaceId'] : each for each in airports}.values()
    airports_id = [elem['PlaceId'] for elem in airports_unique]
    # print(airports_id)
    return airports_id

def __get_country_code(country):
    '''Converts a country into skyscanner ID'''

    endpoint = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/countries/en-US" 
    headers["X-RapidAPI-Host"] = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    
    response = requests.get(endpoint, headers=headers).json()

    while not __check_response(response.text):
        requests.get(endpoint, headers=headers)
    
    response = response.json()

    country_code = [item['Code'] for item in response['Countries'] if item['Name'] == country][0]
    return country_code


def get_routes(origin, destination, outbound_date, inbound_date='', n=3):
    '''Get airplane routes between two cities. Note that a city may have multiple airports'''

    origin_airports = get_airports(origin)[0]
    destination_airports = get_airports(destination)[0]

    endpoint = ("https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/{}/{}/en-US/".format(
                configcountry, configcurrency) +
                origin_airports + '/' + destination_airports + '/' + 'anytime')
            
    headers["X-RapidAPI-Host"] = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    params = {'inboundpartialdate': inbound_date}

    response = requests.get(endpoint, headers=headers, params = params)
    while not __check_response(response.text):
        response = requests.get(endpoint, headers=headers, params = params)

    # We get a list of routes
    routes = response.json()    
    # TODO add check that there exist a route between two cties
    if not routes:
        raise RouteNotFoundException

    return routes