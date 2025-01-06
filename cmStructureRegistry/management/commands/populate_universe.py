import csv
import os
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from cmStructureRegistry.models import Region
from cmStructureRegistry.models import Constellation
from cmStructureRegistry.models import SolarSystem

class Command(BaseCommand):
    help = 'Populate Region, Constellation and Solar Systems'

    def handle(self, *args, **kwargs):


        # Get the absolute path
        current_directory = os.path.dirname(__file__)


        file_path = os.path.join(current_directory, 'data', 'regions.txt')

        # Process Regions
        with open(file_path, newline='') as file:
            reader = csv.reader(file, delimiter="\t")
            for item in reader:

                region, created = Region.objects.update_or_create(
                    id=int(item[0]),
                    defaults = {
                        'name': item[1]
                    }
                )

        file_path = os.path.join(current_directory, 'data', 'constellations.txt')

        # Process Constellations
        with open(file_path, newline='') as file:
            reader = csv.reader(file, delimiter="\t")
            for item in reader:

                constallation, created = Constellation.objects.update_or_create(
                    id=int(item[0]),
                    defaults = {
                        'name': item[1],
                        'region_id': int(item[2])
                    }
                )

        file_path = os.path.join(current_directory, 'data', 'solarsystems.txt')                

        # Process Solarsystems
        with open(file_path, newline='') as file:
            reader = csv.reader(file, delimiter="\t")
            for item in reader:

                solarsystem, created = SolarSystem.objects.update_or_create(
                    id=int(item[0]),
                    defaults = {
                        'name': item[1],
                        'constellation_id': int(item[2]),
                        'x': float(item[3]),
                        'y': float(item[4]),
                        'z': float(item[5]),
                        'security': float(item[6])
                    }
                )                                   


