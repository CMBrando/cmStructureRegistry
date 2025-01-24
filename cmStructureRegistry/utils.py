import requests
from esi.clients import EsiClientProvider
from django.conf import settings

from cmStructureRegistry import app_settings
from cmStructureRegistry import apps

esi = EsiClientProvider(app_info_text=f"{apps.DefaultConfig.verbose_name} v{app_settings.CM_VERSION}")

roman_numerals = [
        "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV",
        "XVI", "XVII", "XVIII", "XIX", "XX"
    ]


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

def get_roman_numeral(number):
    return roman_numerals[int(number) - 1]

