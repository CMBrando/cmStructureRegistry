"""Views."""

from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime, timedelta, timezone
from dateutil import parser
import pytz
import random
import re
import base64
import json

from django.shortcuts import render
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q

# Alliance Auth
from allianceauth.eveonline.models import EveAllianceInfo
from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.framework.api.user import get_main_character_from_user
from allianceauth.services.hooks import get_extension_logger
from esi.models import Token


from .models import TimerType
from .models import TimerStructureType
from .models import TimerHostility
from .models import Region
from .models import SolarSystem
from .models import SolarSystemJump
from .models import Constellation
from .models import CorpTimerView
from .models import CorpTimer
from .models import StructureRegistry
from .models import StructureRegistryView
from .models import StructureRegistryFit
from .models import Corporation
from .models import Alliance
from .models import StructureType

from .forms import CorpTimerForm
from .forms import FleetCommanderForm
from .forms import StructureRegistryForm

from .utils import get_system_api_info
from .utils import get_corporation_api_info
from .utils import get_alliance_api_info
from .utils import solar_system_lookup
from .utils import corporation_lookup
from .utils import get_roman_numeral
from .utils import get_api_notifications
from .utils import get_api_type
from .utils import get_api_planet
from .utils import parse_notification
from .utils import filetime_to_date
from .utils import calculate_lightyears
from .utils import count_jumps
from cmStructureRegistry import app_settings


ANSIBLEX_STRUCTURE_TYPE = 7
POCO_STRUCTURE_TYPE = 18
SKYHOOK_STRUCTURE_TYPE = 19
MERC_STRUCTURE_TYPE = 21

ARMOR_TYPE = 1
HULL_TIMER = 2
IHUB_TIMER = 8
POCO_TYPE = 18

# Get an instance of a logger
logger = get_extension_logger(__name__)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def index(request):
    """Render index view."""
    context = {
        'CM_VERSION': app_settings.CM_VERSION,
    }
    return render(request, "cmStructureRegistry/index.html", context)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def timers(request):
    context = {
        'CM_VERSION': app_settings.CM_VERSION,
    }
    return render(request, "cmStructureRegistry/timers.html", context)      

@login_required
@permission_required("cmStructureRegistry.basic_access")
def timer_types(request):
    items = list(TimerType.objects.all().order_by('name').values())
    return JsonResponse(items, safe=False)
    
@login_required
@permission_required("cmStructureRegistry.basic_access")
def structure_types(request):
    items = list(TimerStructureType.objects.all().order_by('name').values())
    return JsonResponse(items, safe=False)
    
@login_required
@permission_required("cmStructureRegistry.basic_access")
def timer_hostility_types(request):
    items = list(TimerHostility.objects.all().values())
    return JsonResponse(items, safe=False)
   
@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_solar_systems(request):
    query = request.GET.get('query', '')
    items = list(SolarSystem.objects.filter(name__istartswith=query).values())
    return JsonResponse(items, safe=False)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_universe(request):
    query = request.GET.get('query', '')
    items = list(SolarSystem.objects.filter(name__istartswith=query).values())
    items2 = list(Constellation.objects.filter(name__istartswith=query).values())
    items3 = list(Region.objects.filter(name__istartswith=query).values())

    merged_list = list(map(lambda x: {**x, 'name': f"{x['name']} (sys)"}, items)) + \
              list(map(lambda x: {**x, 'name': f"{x['name']} (const)"}, items2)) + \
              list(map(lambda x: {**x, 'name': f"{x['name']} (reg)"}, items3)) 

    return JsonResponse(merged_list, safe=False)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_corps(request):
    query = request.GET.get('query', '')
    items = list(EveAllianceInfo.objects.filter(Q(alliance_name__icontains=query) | Q(alliance_ticker__istartswith=query)).values())
    items2 = list(EveCorporationInfo.objects.filter(Q(corporation_name__icontains=query) | Q(corporation_ticker__istartswith=query)).values())

    merged_list = list(map(lambda x: {**x, 'name': f"{x['alliance_name']} (all)", 'id': f"{x['alliance_id']}"}, items)) + \
              list(map(lambda x: {**x, 'name': f"{x['corporation_name']} (corp)", 'id': f"{x['corporation_id']}"}, items2))

    return JsonResponse(merged_list, safe=False)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_structure(request):
    query = request.GET.get('query', '')
    items = list(StructureRegistryView.objects.filter(structure_name__icontains=query).values())
    items2 = list(TimerStructureType.objects.filter(name__istartswith=query).values())

    merged_list = list(map(lambda x: {**x, 'name': f"{x['structure_name']} (name)", 'id': f"{x['structure_id']}"}, items)) + \
                            list(map(lambda x: {**x, 'name': f"{x['name']} (type)"}, items2))

    return JsonResponse(merged_list, safe=False)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_regions(request):
    query = request.GET.get('query', '')
    items = list(Region.objects.filter(name__istartswith=query).values())
    return JsonResponse(items, safe=False)
      

@login_required
@permission_required("cmStructureRegistry.basic_access")
def get_planets(request):
    system_id = request.GET.get('solarSystemID', '')
    system_data = get_system_api_info(system_id)
    items = list([f'Planet {i+1}' for i in range(len(system_data['planets']))])
    return JsonResponse(items, safe=False) 


@login_required
@permission_required("cmStructureRegistry.manage_timers")
def save_timer(request):

    success = False
    msgs = []

    if request.method == 'POST':
        form = CorpTimerForm(request.POST)

        if form.is_valid():

            utc_now = datetime.now(pytz.utc)
            main_character = get_main_character_from_user(user=request.user)    

            instance = form.save(commit=False)

            # Populate additional fields
            instance.created_by_id = main_character.character_id
            instance.created_date = utc_now
            instance.save()

            return JsonResponse({ 'success': True, 'errors': msgs })
        else:

            msgs = []
            for key in form.errors:
                msgs.append(form.errors[key][0]) # grab the first error message

            return JsonResponse({ 'success': False, 'messages': msgs })
        

@login_required
@permission_required("cmStructureRegistry.basic_access")
def get_open_timers(request):
    current_time_utc = datetime.now(timezone.utc)
    time_60_minutes_ago = current_time_utc - timedelta(minutes=60)

    sel_system = request.GET.get('system')

    items = list(CorpTimerView.objects.filter(timer_datetime__gt=time_60_minutes_ago).values())

    if sel_system:
        for item in items:
            item['jumps'] = count_jumps(int(sel_system), item['system_id'])
            item['distance'] = calculate_lightyears(int(sel_system), item['system_id'])

    return JsonResponse(items, safe=False)

@login_required
@permission_required("cmStructureRegistry.basic_access")
def get_recent_timers(request):

    current_time_utc = datetime.now(timezone.utc)
    time_60_minutes_ago = current_time_utc - timedelta(minutes=60)
    time_14_days_ago = current_time_utc - timedelta(days=14)

    items = list(CorpTimerView.objects.filter(timer_datetime__range=[time_14_days_ago, time_60_minutes_ago]).values())

    return JsonResponse(items, safe=False)    


@login_required
@permission_required("cmStructureRegistry.basic_access")
def get_timer(request):
    id = request.GET.get('id', '')
    items = list(CorpTimerView.objects.filter(id=id).values()) # trying to pull 1 item from django a byzantine mess. not serializable????
    return JsonResponse(items[0], safe=False)


@login_required
@permission_required("cmStructureRegistry.delete_timer")
def delete_timer(request):

    success = False
    msgs = []

    if request.method == 'POST':
        
        timer_id = request.POST.get('timerID', 0)
        result = CorpTimer.objects.filter(pk=timer_id)

        if result:
            instance = result.first()
            instance.delete()
            success = True
        
    return JsonResponse({ 'success': success, 'errors': msgs })
  

@login_required
@permission_required("cmStructureRegistry.manage_timers")
def set_fleetcommander(request):

    success = False
    msgs = []

    if request.method == 'POST':
        form = FleetCommanderForm(request.POST)

        if form.is_valid():

            id = form.data['id']
            fleet_commander = form.data['fleet_commander']

            instance = CorpTimer.objects.get(pk=id)
            instance.fleet_commander = fleet_commander
            instance.save(update_fields=['fleet_commander'])

            return JsonResponse({ 'success': True, 'messages': msgs })
        else:

            msgs = []
            for key in form.errors:
                msgs.append(form.errors[key][0]) # grab the first error message

            return JsonResponse({ 'success': False, 'messages': msgs })


@login_required
@permission_required("cmStructureRegistry.basic_access")
def search_registry(request):

    query = request.GET.get('query', '')
    items = list(StructureRegistry.objects.filter(structure_name__icontains=query).values())
    return JsonResponse(items, safe=False)


@login_required
@permission_required("cmStructureRegistry.basic_access")
def registry_read(request):

    universe = request.GET.get('universe').split(',') if request.GET.get('universe') != '' else []
    corp = request.GET.get('corp').split(',') if request.GET.get('corp') != '' else []
    structure = request.GET.get('structure').split(',') if request.GET.get('structure') != '' else []
    universeItems = []
    corpItems = []
    structureItems = []

    staging_system_id = request.GET.get('staging_system')

    if universe:
        universeItems = list(StructureRegistryView.objects.filter(Q(solar_system_id__in=universe) | Q(constellation_id__in=universe) | Q(region_id__in=universe)).values())

    if corp:
        corpItems = list(StructureRegistryView.objects.filter(Q(corporation_id__in=corp) | Q(alliance_id__in=corp)).values())

    if structure:
        structureItems = list(StructureRegistryView.objects.filter(Q(structure_id__in=structure) | Q(structure_type_id__in=structure)).values())

    items = []
    if universe:
        items.extend(universeItems)

    if corp and items:
        # Merge the lists based on common structures
        items = [
            {**o1, **o2} 
            for o1 in items
            for o2 in corpItems
            if o1['structure_id'] == o2['structure_id']
        ]
    else:
        items.extend(corpItems)

    if structure and items:
        # Merge the lists based on common structures
        items = [
            {**o1, **o2} 
            for o1 in items
            for o2 in structureItems
            if o1['structure_id'] == o2['structure_id']
        ]
    else:
        items.extend(structureItems)


    # no filters passed
    if not universe and not corp and not structure:        
        items = list(StructureRegistryView.objects.values())

    # calc distance
    if staging_system_id:
        for item in items:
            item['jumps'] = count_jumps(int(staging_system_id), item['solar_system_id'])
            item['distance'] = calculate_lightyears(int(staging_system_id), item['solar_system_id'])    
       
    return JsonResponse(items, safe=False)
          
@login_required
@permission_required("cmStructureRegistry.basic_access")
def get_structure(request):

    structure_id = request.GET.get('structureID', 0)

    result = StructureRegistryView.objects.filter(structure_id=structure_id)

    if result:
        items = list(result.values())
        return JsonResponse(items[0], safe=False)       
    else:
        return JsonResponse({}, safe=False)


@login_required
@permission_required("cmStructureRegistry.manage_structures")
def save_structure(request):

    success = False
    msgs = []
    utc_now = datetime.now(timezone.utc)
    main_character = get_main_character_from_user(user=request.user)

    if request.method == 'POST':
        form = StructureRegistryForm(request.POST)

        if form.is_valid():

            structure_id = form.data['structure_id']
            corporation_name = form.data['corporation_name']
            structure_name = form.data['structure_name'].strip()
            structure_type_id = int(form.data['structure_type_id'])
            fit = form.data['fit']  #base64 encoded
            vulnerability = form.data['vulnerability']
            system_id = form.data['system_id'] # for merc den
            planet = form.data['planet'] # for merd den

            corp_result = corporation_lookup(corporation_name)

            # check if there's a distance at the end and strip
            if structure_name.lower().endswith(' km') or structure_name.lower().endswith(' m') or structure_name.lower().endswith(' au'):
                lastIndex = structure_name.rfind(' ')
                structure_name = structure_name[0: structure_name.rfind(" ", 0, lastIndex)].strip()

            if corp_result:

                index = structure_name.find(" - ")

                if structure_type_id == ANSIBLEX_STRUCTURE_TYPE:
                    index = structure_name.find(" » ")

                solar_system_name = ""    

                # check for special parsing on POCO, Skyhook and Mercenary Den
                if index == -1 and int(structure_type_id) in [POCO_STRUCTURE_TYPE, SKYHOOK_STRUCTURE_TYPE, MERC_STRUCTURE_TYPE]:
                    pattern = r"\(([^)]+)\)|\[([^\]]+)\]"
                    matches = re.findall(pattern, structure_name)
                    results = [match[0] or match[1] for match in matches] 

                    if len(results) == 2:
                        structure_name = structure_name.replace("[" + results[1] + "]", "") # strip the corp name from the end)
                        index = results[0].rfind(" ")
                        solar_system_name = results[0][0:index].strip()
                    elif len(results) == 1:
                        index = results[0].rfind(" ")
                        solar_system_name = results[0][0:index].strip()
                    elif not structure_id and structure_type_id == MERC_STRUCTURE_TYPE:
                        solar_system_name = None  # do nothing when adding a merc, additional logic below
                    else:
                        msgs.append("Could not identify Solar System from Structure Name")
                else:
                    solar_system_name = structure_name[0:index].strip()

                # handle merc den if adding structure
                if not structure_id and structure_type_id == MERC_STRUCTURE_TYPE and (not system_id or not planet):
                    msgs.append("System and Planet are required for Mercenary Den")
                    return JsonResponse({ 'success': success, 'messages': msgs })
                elif not structure_id and structure_type_id == MERC_STRUCTURE_TYPE:
                    system_result = get_system_api_info(system_id)
                    if system_result:
                        solar_system_name = system_result['name']
                        planet_num = planet[-1 * (len(planet) - planet.rfind(' ')):] # planet X
                        roman_planet = get_roman_numeral(planet_num)
                        structure_name = f"{structure_name} ({solar_system_name} {roman_planet})"


                if solar_system_name or system_id: 

                    system_result = solar_system_lookup(solar_system_name)
                
                    if system_result:
                        registry = form.instance
                        registry.structure_id = structure_id if structure_id else int('9' + ''.join([str(random.randint(0, 9)) for _ in range(12)])) # if new structure generate a random id
                        registry.structure_name = structure_name
                        registry.solar_system_id = system_result['id'] if system_result else system_id
                        registry.corporation_id = corp_result['id']
                        registry.removed = False

                        # update or add corporation and alliance
                        corp_api_result = get_corporation_api_info(registry.corporation_id)

                        eve_alliance = None
                        alliance_id = corp_api_result.get('alliance_id')
                        if alliance_id:
                            alliance_api_result = get_alliance_api_info(alliance_id)
                            eve_alliance, created = EveAllianceInfo.objects.update_or_create(
                            alliance_id = alliance_id,
                            defaults = {
                                'alliance_name': alliance_api_result.get('name'),
                                'alliance_ticker': alliance_api_result.get('ticker'),
                                'executor_corp_id': alliance_api_result.get('executor_corporation_id')
                            }
                         )

                        eve_corporation, created = EveCorporationInfo.objects.update_or_create(
                            corporation_id= registry.corporation_id,
                            defaults = {
                                'corporation_name': corp_api_result.get('name'),
                                'corporation_ticker': corp_api_result.get('ticker'),
                                'member_count': corp_api_result.get('member_count'),
                                'ceo_id': corp_api_result.get('ceo_id'),
                                'alliance': eve_alliance
                            }
                         )  

                        if vulnerability:
                            registry.vulnerability = vulnerability
                            registry.vulnerability_updated = utc_now
                            registry.vulnerability_character_id = main_character.character_id  

                        # save stucture at the end
                        registry.save()
                        success = True

                        # if fit passed, save as well.
                        if fit:
                            bytes = base64.b64decode(fit)
                            fit_json_raw = bytes.decode("utf-8")  # Convert bytes to string

                            fit_instance = StructureRegistryFit()
                            fit_instance.structure_id = registry.structure_id
                            fit_instance.fit_json = fit_json_raw
                            fit_instance.modified_date = utc_now
                            fit_instance.character_id = main_character.character_id
                            fit_instance.save()

                    else:            
                        msgs.append("Could not identify Solar System from Structure Name")
                else:            
                    msgs.append("Could not identify Solar System from Structure Name")                        
                
            else:
                msgs.append("Could not identify corporation");
        else:

            msgs = []
            for key in form.errors:
                msgs.append(form.errors[key][0]) # grab the first error message


        return JsonResponse({ 'success': success, 'messages': msgs })
    

@login_required
@permission_required("cmStructureRegistry.manage_structures")
def save_structure_fit(request):

    success = False
    msgs = []

    structure_id = request.GET.get('structureID', 0)

    if request.method == 'POST':
        
        body = request.body
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            msgs.append('Invalid JSON')
            return JsonResponse({ 'success': False, 'messages': msgs })
        
        utc_now = datetime.now(timezone.utc)
        main_character = get_main_character_from_user(user=request.user)

        result = StructureRegistryFit.objects.filter(pk=structure_id)

        if not result:
            instance = StructureRegistryFit()
            instance.structure_id = structure_id
            instance.fit_json = json.dumps(data) #save the raw json
            instance.modified_date = utc_now
            instance.character_id = main_character.character_id
            instance.save()
        else:
            instance = result.first()
            instance.fit_json = json.dumps(data) #save the raw json
            instance.modified_date = utc_now
            instance.character_id = main_character.character_id         
            instance.save(update_fields=['fit_json', 'modified_date', 'character_id'])

        return JsonResponse({ 'success': True, 'errors': msgs })
    

@login_required
@permission_required("cmStructureRegistry.manage_structures")
def save_structure_vuln(request):

    success = False
    msgs = []

    if request.method == 'POST':
        
        structure_id = request.POST.get('structureID', 0)
        vuln = request.POST.get('vulnerability')
        
        utc_now = datetime.now(timezone.utc)
        main_character = get_main_character_from_user(user=request.user)

        result = StructureRegistry.objects.filter(pk=structure_id)

        if result:
            instance = result.first()
            instance.vulnerability = vuln
            instance.vulnerability_updated = utc_now
            instance.vulnerability_character_id = main_character.character_id         
            instance.save(update_fields=['vulnerability', 'vulnerability_updated', 'vulnerability_character_id'])
            success = True

        
    return JsonResponse({ 'success': success, 'errors': msgs })


@login_required
@permission_required("cmStructureRegistry.delete_structure")
def delete_structure(request):

    success = False
    msgs = []

    if request.method == 'POST':
        
        structure_id = request.POST.get('structureID', 0)
        result = StructureRegistry.objects.filter(pk=structure_id)

        if result:
            instance = result.first()

            # check for fit and delete first
            res_fit = StructureRegistryFit.objects.filter(pk=structure_id)

            if res_fit:
                fit_instance = res_fit.first()
                fit_instance.delete()

            instance.delete()
            success = True

        
    return JsonResponse({ 'success': success, 'errors': msgs })










    
       