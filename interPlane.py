'''
A python script to search for economic flights in anonimous using Tor and Skyscanner.
To use skyscanner you have to register an api-key in config.py refer to: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
'''

import smtplib
import re
import numpy as np
from sympy.utilities.iterables import multiset_permutations
import traceback

from RouteException import RouteNotFoundException
import skyscannerWrapper

# from skyscannerWrapper import *

# TODO
# · Weight flight time
# · How to report the results?


def compute_cost_time(origin: str, destination: str, outbound_date = 'Anytime')->[int,int]:
    """Computes the cost and time of going from origin to destination cities using an airplane

    Args:
        origin (str): Origin city
        destination (str): Destination city
        outbound_date (str, optional): When to depart. Defaults to 'Anytime'.

    Returns:
        [int,int]: cost and time
    """    

    # TODO how to get the flight time?
    
    print('Getting planes from {} TO {} ...'.format(origin, destination))
    try:
        routes = skyscannerWrapper.get_routes(origin, destination, outbound_date)
        minimum_cost = routes['Quotes'][0]['MinPrice']
        time = 10
    except RouteNotFoundException:
        print('- There no route from {} TO {}'.format(origin, destination))
        minimum_cost = 99999
    except Exception as e:
        print(e)
    finally:
        return minimum_cost, time


def get_cheapest_route(cities: [], weight_time = 0):
    '''
    Given a list of cities returns the cheapest air route order to travel them
    Example: 
        Given [Berlin, London, Zurich, Prague], it may be cheaper to fly in this order[London, Zurich, Berlin, Prague]
    

    Args:
        cities[]: array of cities name
        weight_time int: integer to weight the flight time 
    You 
    # TODO how to manage time? IDEA, givena start and end day of the trip. A minimum amount of days in each city and some tolerance
    '''

    # TODO remove the first city (which is the actual origin)
    # TODO add roundtrip option
    
    n = len(cities)
    cost = -1*np.ones((n,n)) # cost matrix

    min_cost = 0
    best_idx = 0
    cities_permutations = [perm for perm in multiset_permutations(cities)]
    for idx, city_perm in enumerate(cities_permutations):
        perm_cost = 0
        for i in range(n-1):
            j = i + 1
            origin, destination = city_perm[i], city_perm[j]
            i, j = cities.index(origin), cities.index(destination)
            if cost[i][j] == -1:
                cost[i][j], time = compute_cost_time(origin, destination)
            perm_cost += cost[i][j]

        if perm_cost < min_cost:
            min_cost = perm_cost
            best_idx = idx
    
    return cities_permutations[best_idx]


