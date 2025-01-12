"""Views."""

from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime, timedelta, timezone
import pytz
import random
import re

from django.shortcuts import render
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q

# Alliance Auth
from allianceauth.framework.api.user import get_main_character_from_user

from .models import TimerType
from .models import TimerStructureType
from .models import TimerHostility
from .models import Region
from .models import SolarSystem
from .models import CorpTimerView
from .models import CorpTimer
from .models import StructureRegistry
from .models import StructureRegistryView
from .models import StructureRegistryFit
from .models import Corporation
from .models import Alliance

from .forms import CorpTimerForm
from .forms import FleetCommanderForm
from .forms import StructureRegistryForm

from .utils import get_system_api_info
from .utils import get_corporation_api_info
from .utils import get_alliance_api_info
from .utils import solar_system_lookup
from .utils import corporation_lookup
from cmStructureRegistry import app_settings

import logging
import json

ANSIBLEX_STRUCTURE_TYPE = 7

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
@permission_required("cmStructureRegistry.view_structureregistry")
def index(request):
    """Render index view."""
    context = {
        'CM_VERSION': app_settings.CM_VERSION,
    }
    return render(request, "cmStructureRegistry/index.html", context)

@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def timers(request):
    context = {
        'CM_VERSION': app_settings.CM_VERSION,
    }
    return render(request, "cmStructureRegistry/timers.html", context)      

@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def timer_types(request):
    items = list(TimerType.objects.all().values())
    return JsonResponse(items, safe=False)
    
@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def structure_types(request):
    items = list(TimerStructureType.objects.all().values())
    return JsonResponse(items, safe=False)
    
@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def timer_hostility_types(request):
    items = list(TimerHostility.objects.all().values())
    return JsonResponse(items, safe=False)
   
@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def search_solar_systems(request):
    query = request.GET.get('query', '')
    items = list(SolarSystem.objects.filter(name__istartswith=query).values())
    return JsonResponse(items, safe=False)

@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def search_regions(request):
    query = request.GET.get('query', '')
    items = list(Region.objects.filter(name__istartswith=query).values())
    return JsonResponse(items, safe=False)
      

@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def get_planets(request):
    system_id = request.GET.get('solarSystemID', '')
    system_data = get_system_api_info(system_id)
    items = list([f'Planet {i+1}' for i in range(len(system_data['planets']))])
    return JsonResponse(items, safe=False) 


@login_required
@permission_required("cmStructureRegistry.add_corptimer")
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
@permission_required("cmStructureRegistry.view_corptimer")
def get_open_timers(request):
    current_time_utc = datetime.now(timezone.utc)
    time_100_minutes_ago = current_time_utc - timedelta(minutes=100)

    items = list(CorpTimerView.objects.filter(timer_datetime__gt=time_100_minutes_ago).values())
    return JsonResponse(items, safe=False)

@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def get_recent_timers(request):
    current_time_utc = datetime.now(timezone.utc)
    time_100_minutes_ago = current_time_utc - timedelta(minutes=100)
    time_14_days_ago = current_time_utc - timedelta(days=14)

    items = list(CorpTimerView.objects.filter(timer_datetime__range=[time_14_days_ago, time_100_minutes_ago]).values())
    return JsonResponse(items, safe=False)    


@login_required
@permission_required("cmStructureRegistry.view_corptimer")
def get_timer(request):
    id = request.GET.get('id', '')
    items = list(CorpTimerView.objects.filter(id=id).values()) # trying to pull 1 item from django a byzantine mess. not serializable????
    return JsonResponse(items[0], safe=False)


@login_required
@permission_required("cmStructureRegistry.delete_corptimer")
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
@permission_required("cmStructureRegistry.change_corptimer")
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
@permission_required("cmStructureRegistry.view_structureregistry")
def search_registry(request):

    query = request.GET.get('query', '')
    items = list(StructureRegistry.objects.filter(structure_name__icontains=query).values())
    return JsonResponse(items, safe=False)


@login_required
@permission_required("cmStructureRegistry.view_structureregistry")
def registry_read(request):

    term = request.GET.get('term', '')
    region_id = request.GET.get('regionId', 0)
    items = []

    if region_id != '0':
        items = list(StructureRegistryView.objects.filter(Q(region_id=region_id) & (Q(structure_name__icontains=term) | Q(structure_type__icontains=term) | Q(alliance__icontains=term) | Q(corporation__icontains=term) | Q(constellation__icontains=term))).values())
    elif term != '':
        items = list(StructureRegistryView.objects.filter(Q(structure_name__icontains=term) | Q(structure_type__icontains=term) | Q(alliance__icontains=term) | Q(corporation__icontains=term) | Q(constellation__icontains=term)).values())
    else:
        items = list(StructureRegistryView.objects.values())

       
    return JsonResponse(items, safe=False)
          
@login_required
@permission_required("cmStructureRegistry.view_structureregistry")
def get_structure(request):

    structure_id = request.GET.get('structureID', 0)

    result = StructureRegistryView.objects.filter(structure_id=structure_id)

    if result:
        items = list(result.values())
        return JsonResponse(items[0], safe=False)       
    else:
        return JsonResponse({}, safe=False)


@login_required
@permission_required("cmStructureRegistry.add_structureregistry")
def save_structure(request):

    success = False
    msgs = []

    if request.method == 'POST':
        form = StructureRegistryForm(request.POST)

        if form.is_valid():

            structure_id = form.data['structure_id']
            corporation_name = form.data['corporation_name']
            structure_name = form.data['structure_name'].strip()
            structure_type_id = int(form.data['structure_type_id'])

            corp_result = corporation_lookup(corporation_name)

            # check if there's a distance at the end and strip
            if structure_name.endswith(' km') or structure_name.endswith(' m'):
                lastIndex = structure_name.rfind(' ')
                structure_name = structure_name[0: structure_name.rfind(" ", 0, lastIndex)].strip()

            if corp_result:

                index = structure_name.find(" - ")

                if structure_type_id == ANSIBLEX_STRUCTURE_TYPE:
                    index = structure_name.find(" » ")

                solar_system_name = ""    

                if index == -1:
                    # check if legacy POCO
                    pattern = r"\(([^)]+)\)|\[([^\]]+)\]"
                    matches = re.findall(pattern, structure_name)
                    results = [match[0] or match[1] for match in matches] 

                    if len(results) == 2:
                        structure_name = structure_name.replace("[" + results[1] + "]", "") # strip the corp name from the end)
                        index = results[0].rfind(" ")
                        solar_system_name = results[0][0:index].strip()
                    else:
                        msgs.append("Could not identify Solar System from Structure Name")
                else:
                    solar_system_name = structure_name[0:index]

                if solar_system_name: 

                    system_result = solar_system_lookup(solar_system_name)
                
                    if system_result:
                        registry = form.instance
                        registry.structure_id = structure_id if structure_id else int('9' + ''.join([str(random.randint(0, 9)) for _ in range(12)])) # if new structure generate a random id
                        registry.structure_name = structure_name  # in case string was trimmed earlier
                        registry.solar_system_id = system_result['id']
                        registry.corporation_id = corp_result['id']
                        registry.removed = False

                        # update or add corporation
                        corp_api_result = get_corporation_api_info(registry.corporation_id)

                        corp = Corporation.objects.filter(corporation_id=registry.corporation_id)
                        if len(corp) == 0:
                            new_corp = Corporation(corporation_id = registry.corporation_id, name = corp_api_result.get('name'), ticker = corp_api_result.get('ticker'), alliance_id = corp_api_result.get('alliance_id'))
                            new_corp.save()
                        else:
                            corp_instance = corp.first()
                            corp_instance.alliance_id = corp_api_result.get('alliance_id')
                            corp_instance.save()

                        alliance_id = corp_api_result.get('alliance_id')

                        alliance = Alliance.objects.filter(alliance_id=alliance_id)
                        if alliance_id and len(alliance) == 0:
                            alliance_api_result = get_alliance_api_info(alliance_id)
                            new_alliance = Alliance(alliance_id = alliance_id, name = alliance_api_result['name'], ticker = alliance_api_result['ticker'])
                            new_alliance.save()

                        # save stucture at the end
                        registry.save()
                        success = True    

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
@permission_required("cmStructureRegistry.change_structureregistry")
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
@permission_required("cmStructureRegistry.change_structureregistry")
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
@permission_required("cmStructureRegistry.delete_structureregistry")
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








    
       