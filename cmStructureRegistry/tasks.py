"""Tasks."""

from celery import shared_task

from datetime import datetime, timedelta, timezone
import pytz
import yaml

from django.http import JsonResponse
from django.db.models import Q
from django.db.models import F, Window
from django.db.models.functions import RowNumber

from .models import TimerStructureType
from .models import CorpTimer

from .utils import get_api_structure
from .utils import get_api_planet
from .utils import get_api_sovereignty_structures
from .utils import filetime_to_date

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from esi.models import Token


CORPTOOLS_DEP = False

# Corp Tools (optional, only for friendly timer creations)
try:
    from corptools.models import Notification
    from corptools.models import NotificationText
    from eveuniverse.models import EveType
    CORPTOOLS_DEP = True
except ImportError:
    CORPTOOLS_DEP = False

from cmStructureRegistry import app_settings


logger = get_extension_logger(__name__)

ANSIBLEX_STRUCTURE_TYPE = 7
POCO_STRUCTURE_TYPE = 18
SKYHOOK_STRUCTURE_TYPE = 19
MERC_STRUCTURE_TYPE = 21
POS_TYPE = 12
SOV_HUB_TYPE = 22

ARMOR_TYPE = 1
HULL_TIMER = 2
IHUB_TIMER = 6
TCU_TIMER = 7
ENT_TIMER = 10



@shared_task
def notification_timer_task():

    try:

        if CORPTOOLS_DEP:

            wanted_types = ["SovStructureReinforced", "OrbitalReinforced", "MercenaryDenReinforced", "SkyhookLostShields", "StructureLostShields", "StructureLostArmor"  ]
            cutoff = datetime.now(timezone.utc) - timedelta(days=3)
            utc_now = datetime.now(pytz.utc)

            qs = (
                Notification.objects
                .filter(
                    notification_type__in=wanted_types,
                    timestamp__gte=cutoff,
                )
                .annotate(
                    rn=Window(
                        expression=RowNumber(),
                        partition_by=[F("timestamp")],
                        order_by=[F("notification_id").asc(), F("character_id").asc()]
                    )
                )
                .filter(rn=1)
                .order_by("notification_id")
            )

            notifications = qs

            access_token = None

            sov_structures = get_api_sovereignty_structures()

            not_count = len(notifications)
            logger.info(f"Notifications Found: {not_count}")

            for notification in notifications:
                result = CorpTimer.objects.filter(notification_id=notification.notification_id)

                if not result:

                    not_text = NotificationText.objects.filter(notification_id=notification.notification_id)

                    if not_text:
                        
                        msg = "found not text"
                        not_entry = not_text.first()

                        item = yaml.safe_load(not_entry.notification_text)

                        char = EveCharacter.objects.get(pk=notification.character_id)

                        # if there is a filter defined for corps check it.
                        if hasattr(app_settings, 'FRIENDLY_TIMER_CORP_IDS'):
                            if char.corporation_id not in app_settings.FRIENDLY_TIMER_CORP_IDS:
                                continue

                        if not access_token:
                            token_res = Token.get_token(char.character_id, scopes=[
                                "esi-universe.read_structures.v1",
                            ])

                            access_token = token_res.valid_access_token()


                        not_type = notification.notification_type
                        
                        if not_type == "SovStructureReinforced":
                            
                            campaign_type = item.get("campaignEventType", None);
                        
                            if campaign_type == 2: # SOV

                                solar_system = item["solarSystemID"]

                                match = next(
                                    (item for item in sov_structures if item.get("solar_system_id") == solar_system),
                                    None
                                )
                            
                                # if alliance owns sov then save as friendly
                                if match and match.get('alliance_id') == char.alliance_id:

                                    timer_datetime = filetime_to_date(item["decloakTime"])

                                    instance = CorpTimer()
                                    instance.system_id = solar_system
                                    instance.timer_type_id = ENT_TIMER
                                    instance.timer_datetime = timer_datetime
                                    instance.created_by_id = char.character_id
                                    instance.created_date = utc_now
                                    instance.hostility_type_id = 2  #  Friendly
                                    instance.structure_type_id = SOV_HUB_TYPE
                                    instance.notification_id = notification.notification_id
                                    instance.save()  

                        elif not_type == "OrbitalReinforced":
                            planet_id = item.get("planetID", None)

                            msg = "found orbital"

                            timer_datetime = filetime_to_date(item["reinforceExitTime"])

                            #every orbital associated with planet so only proceed if found
                            if planet_id:
                                planet_result = get_api_planet(planet_id)

                                instance = CorpTimer()
                                instance.system_id = item["solarSystemID"]
                                instance.timer_type_id = ARMOR_TYPE
                                instance.timer_datetime = timer_datetime
                                instance.planet = planet_result["name"]
                                instance.created_by_id = char.character_id
                                instance.created_date = utc_now
                                instance.hostility_type_id = 2  #  Friendly
                                instance.structure_type_id = POCO_STRUCTURE_TYPE
                                instance.notification_id = notification.notification_id
                                instance.save()

                        elif not_type == "MercenaryDenReinforced":

                            planet_id = item.get("planetID", None)

                            msg = "found merc"

                            timer_datetime = filetime_to_date(item["timestampExited"])

                            structure = None
                            try:
                                structure = get_api_structure(item["itemID"], access_token)    
                            except Exception:
                                pass

                            if planet_id:
                                planet_result = get_api_planet(planet_id)

                                instance = CorpTimer()
                                instance.system_id = item["solarsystemID"]
                                instance.timer_type_id = ARMOR_TYPE
                                instance.timer_datetime = timer_datetime
                                instance.planet = planet_result["name"]
                                instance.created_by_id = char.character_id
                                instance.created_date = utc_now
                                instance.hostility_type_id = 2  #  Friendly
                                instance.structure_type_id = MERC_STRUCTURE_TYPE
                                instance.comment = structure["name"] if structure else ""
                                instance.notification_id = notification.notification_id
                                instance.save()                        

                        elif notification.notification_type == "SkyhookLostShields":

                            msg = "found skyhook not type"

                            planet_id = item.get("planetID", None)

                            structure = None
                            try:
                                structure = get_api_structure(item["itemID"], access_token)    
                            except Exception:
                                pass

                            if planet_id:

                                planet_result = get_api_planet(planet_id)

                                timer_datetime = filetime_to_date(item["timestamp"])

                                instance = CorpTimer()
                                instance.system_id = item["solarsystemID"]
                                instance.timer_type_id = ARMOR_TYPE
                                instance.timer_datetime = timer_datetime
                                instance.created_by_id = char.character_id
                                instance.created_date = utc_now
                                instance.hostility_type_id = 2  #  Friendly
                                instance.comment = structure["name"] if structure else ""
                                instance.structure_type_id = SKYHOOK_STRUCTURE_TYPE
                                instance.notification_id = notification.notification_id
                                instance.save()      


                        elif notification.notification_type == "StructureLostShields" or notification.notification_type == "StructureLostArmor":

                            msg = "found stucture not type"

                            type_result = EveType.objects.get(id=item["structureTypeID"])

                            if type_result:
                                msg = "found type result: "

                                # we do a contains check because Metenox has multiple types
                                timer_structure_type = next(
                                    (obj for obj in TimerStructureType.objects.all() if obj.name and obj.name.lower() in type_result.name.lower()),
                                    None
                                )

                                timer_type = None
                                if not_type == "StructureLostShields":
                                    timer_type = ARMOR_TYPE
                                else:
                                    timer_type = HULL_TIMER

                                structure = None
                                try:
                                    structure = get_api_structure(item["structureID"], access_token)    
                                except Exception:
                                    pass                                

                                if timer_structure_type:

                                    msg = "found api structure"

                                    timer_datetime = filetime_to_date(item["timestamp"])

                                    instance = CorpTimer()
                                    instance.system_id = item["solarsystemID"]
                                    instance.timer_type_id = timer_type
                                    instance.timer_datetime = timer_datetime
                                    instance.created_by_id = char.character_id
                                    instance.created_date = utc_now
                                    instance.hostility_type_id = 2  #  Friendly
                                    instance.comment = structure["name"] if structure else ""
                                    instance.structure_type_id = timer_structure_type.id
                                    instance.notification_id = notification.notification_id
                                    instance.save()                  
    except Exception as e:
        logger.exception(f"Notification timer creation failed: {e}")    