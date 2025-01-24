import csv
import os
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from allianceauth.eveonline.models import EveAllianceInfo
from allianceauth.eveonline.models import EveCorporationInfo

from cmStructureRegistry.utils import get_alliance_api_info
from cmStructureRegistry.utils import get_corporation_api_info

from cmStructureRegistry.models import Alliance
from cmStructureRegistry.models import Corporation


class Command(BaseCommand):
    help = 'Migrates CM Corporation and Alliance entries to AA tables'

    def handle(self, *args, **kwargs):
                        
        alliances = Alliance.objects.all()                        
        for alliance in alliances:

            alliance_api_result = get_alliance_api_info(alliance.alliance_id)

            eve_alliance, created = EveAllianceInfo.objects.update_or_create(
                alliance_id = alliance.alliance_id,
                defaults = {
                    'alliance_name': alliance_api_result.get('name'),
                    'alliance_ticker': alliance_api_result.get('ticker'),
                    'executor_corp_id': alliance_api_result.get('executor_corporation_id')
                }            
            )

        corporations = Corporation.objects.all()
        for corporation in corporations:
            corp_api_result = get_corporation_api_info(corporation.corporation_id)                            

            eve_alliance = None
            if corp_api_result.get('alliance_id'):
                alliance_id = corp_api_result.get('alliance_id')
                eve_alliance = EveAllianceInfo.objects.get(alliance_id=alliance_id)

            eve_corporation, created = EveCorporationInfo.objects.update_or_create(
                corporation_id= corporation.corporation_id,
                defaults = {
                    'corporation_name': corp_api_result.get('name'),
                    'corporation_ticker': corp_api_result.get('ticker'),
                    'member_count': corp_api_result.get('member_count'),
                    'ceo_id': corp_api_result.get('ceo_id'),
                    'alliance': eve_alliance
                }
            )

        
