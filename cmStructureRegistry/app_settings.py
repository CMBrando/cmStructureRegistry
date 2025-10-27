"""App settings."""

from django.conf import settings

from cmStructureRegistry import __version__ as CM_VERSION

FRIENDLY_TIMER_CORP_IDS = getattr(settings, "FRIENDLY_TIMER_CORP_IDS", [])
