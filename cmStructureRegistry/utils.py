import requests
import math
import json
import pickle
from collections import deque
from datetime import datetime, timedelta
from esi.clients import EsiClientProvider
from django.conf import settings
from allianceauth.utils.cache import get_redis_client
from allianceauth.services.hooks import get_extension_logger

from cmStructureRegistry import app_settings
from cmStructureRegistry import apps
from .models import SolarSystemJump
from .models import SolarSystem

logger = get_extension_logger(__name__)
esi = EsiClientProvider(app_info_text=f"{apps.DefaultConfig.verbose_name} v{app_settings.CM_VERSION}")

EPOCH_AS_FILETIME = 116444736000000000
ROMAN_NUMERALS = [
        "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV",
        "XVI", "XVII", "XVIII", "XIX", "XX",
        "XXI", "XXII", "XXIII", "XXIV", "XXV"
    ]

JUMP_KEY_CACHE = 172800

METERS_PER_LIGHT_YEAR = 9.461e+15


def get_system_api_info(system_id):
    return esi.client.Universe.get_universe_systems_system_id(system_id=system_id).results()

def solar_system_lookup(solar_system_name):
    result = esi.client.Universe.post_universe_ids(names=[solar_system_name]).results()
    systems = result.get('systems',[])
    if systems and len(systems) == 1:
        return systems[0]
    else:
        return None

def corporation_lookup(corporation_name):
    result = esi.client.Universe.post_universe_ids(names=[corporation_name]).results()
    systems = result.get('corporations',[])
    if systems and len(systems) == 1:
        return systems[0]
    else:
        return None

def get_corporation_api_info(corporation_id):
    return esi.client.Corporation.get_corporations_corporation_id(corporation_id=corporation_id).result()       

def get_alliance_api_info(alliance_id):
    return esi.client.Alliance.get_alliances_alliance_id(alliance_id=alliance_id).result()

def get_api_type(type_id):
    return esi.client.Universe.get_universe_types_type_id(type_id=type_id).result()

def get_api_planet(planet_id):
    return esi.client.Universe.get_universe_planets_planet_id(planet_id = planet_id).result()

def get_api_notifications(character_id, token):
    return esi.client.Character.get_characters_character_id_notifications(
        character_id = character_id,
        token = token
    ).results()
    

def get_roman_numeral(number):
    return ROMAN_NUMERALS[int(number) - 1]

def calculate_lightyears(start_system_id, end_system_id):
    start_system = list(SolarSystem.objects.filter(id=start_system_id).values())
    end_system = list(SolarSystem.objects.filter(id=end_system_id).values())

    if start_system and end_system:
        x1 = start_system[0].get('x')
        y1 = start_system[0].get('y')        
        z1 = start_system[0].get('z')

        x2 = end_system[0].get('x')
        y2 = end_system[0].get('y')        
        z2 = end_system[0].get('z')

        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance / METERS_PER_LIGHT_YEAR
    else:
        return -1


def count_jumps(start, target):

    cache = get_redis_client()

    key = f"cmDistance_{start}_{target}"
    jump_cache = cache.get(key)

    if jump_cache:
        return int(jump_cache)

    start = str(start)
    target = str(target)       

    graph = None
    graph_cache = cache.get('cm_system_graph')

    if graph_cache:
        graph = json.loads(graph_cache)

    if not graph:
        graph = {}
        mappings = list(SolarSystemJump.objects.all().values())        

        # Build adjacency list
        for mapping in mappings:

            # pull as strings can json serialization will convert anyways
            from_solar_system_id = str(mapping.get('from_solar_system_id'))
            to_solar_system_id = str(mapping.get('to_solar_system_id'))

            if from_solar_system_id not in graph:
                graph[from_solar_system_id] = []
            graph[from_solar_system_id].append(to_solar_system_id)

        cache.set('cm_system_graph', json.dumps(graph), JUMP_KEY_CACHE) # Save the cache

    queue = deque([(start, 0)])
    visited = set()

    while queue:
        current, jumps = queue.popleft()

        if current == target:
            cache.set(key, jumps, JUMP_KEY_CACHE)
            return jumps

        if current in visited:
            continue
        visited.add(current)

        for neighbor in graph.get(str(current), []):
            queue.append((neighbor, jumps + 1))

    return -1  # Target not reachable

def parse_notification(text: str) -> dict:
    parsed_dict = {}

    lines = text.split('\n')
    for line in lines:
        # Skip lines with no colon to delineate name/value
        if ':' not in line:
            continue

        name_val = line.split(':', 1)  # Limit split to 2 parts
        name = name_val[0].strip()
        val = name_val[1].replace("&id001", "").replace("*id001", "").strip()

        if name not in parsed_dict:
            parsed_dict[name] = val

    return parsed_dict

def filetime_to_date(ft):
    us = (ft - EPOCH_AS_FILETIME) // 10
    return datetime(1970, 1, 1) + timedelta(microseconds = us)      

