"""Models."""

from django.db import models

class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        cmStructureRegistry :: Meta
        """
        managed = False
        default_permissions = ()
        permissions = (
            # can access and register his own participation to a FAT link
            ("basic_access", ("Can view structure registry and timers")),
            ("manage_structures", ("Can add structures and set fits and vulnerabilities")),
            ("manage_timers", ("Can add timers and set FCs")),
            ("delete_structure", ("Can remove structures")),
            ("delete_timer", ("Can delete timer"))
        )
        verbose_name = ("cmStructureRegistry")


class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        default_permissions = ()
        db_table = "cm_region" 

class Constellation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    region_id = models.IntegerField()

    class Meta:
        default_permissions = ()                        
        db_table = "cm_constellation" 

class SolarSystem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    constellation_id = models.IntegerField()
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    security = models.FloatField(null=True)

    class Meta:
        default_permissions = ()        
        db_table = "cm_solar_system" 

class TimerType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        default_permissions = ()        
        db_table = "cm_timer_type"
  
class TimerHostility(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "cm_timer_hostility"

class TimerStructureType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        default_permissions = ()        
        db_table = "cm_timer_structure_type"

class CorpTimer(models.Model):
    id = models.AutoField(primary_key=True)
    system_id = models.BigIntegerField(blank=False, null=False)
    timer_type_id = models.IntegerField(blank=False, null=False)   
    timer_datetime = models.DateTimeField(blank=False, null=False)
    comment = models.CharField(blank=True, max_length=1000)
    created_by_id = models.BigIntegerField()
    created_date = models.DateTimeField()
    hostility_type_id = models.IntegerField(blank=True, null=True)    
    structure_type_id = models.IntegerField(blank=True, null=True)
    structure_id = models.BigIntegerField(blank=True, null=True)
    fleet_commander = models.CharField(blank=True, max_length=255, null=True)
    planet = models.CharField(blank=True, max_length=255, null=True)

    class Meta:
        default_permissions = ()        
        db_table = "cm_corp_timer"

class StructureType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        default_permissions = ()        
        db_table = "cm_structure_type"

class Alliance(models.Model):
    alliance_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=50)

    class Meta:
        default_permissions = ()        
        db_table = "cm_alliance"      

class Corporation(models.Model):
    corporation_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=50)
    alliance_id = models.IntegerField(blank=True, null=True)

    class Meta:
        default_permissions = ()        
        db_table = "cm_corporation"


class StructureRegistry(models.Model):
    structure_id = models.BigIntegerField(primary_key=True)
    structure_name = models.CharField(blank=False, null=False, max_length=1000)
    structure_type_id = models.IntegerField(blank=False, null=False)
    solar_system_id = models.IntegerField(blank=False, null=False)   
    corporation_id = models.IntegerField(blank=False, null=False)
    removed = models.BooleanField(blank=False, null=False)
    removed_date = models.DateTimeField(blank=True, null=True)
    vulnerability = models.CharField(blank=True, max_length=10, null=True)    
    vulnerability_updated = models.DateTimeField(blank=True, null=True)
    vulnerability_character_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        default_permissions = ()        
        db_table = "cm_structure_registry"   
       
class StructureRegistryFit(models.Model):
    structure_id = models.BigIntegerField(primary_key=True)
    fit_json = models.TextField(blank=False, null=False)
    modified_date = models.DateTimeField(blank=False, null=False)
    character_id = models.BigIntegerField(blank=False, null=False)

    class Meta:
        default_permissions = ()        
        db_table = "cm_structure_registry_fit"


class CorpTimerView(models.Model):
    id = models.IntegerField(primary_key=True)
    system_id = models.BigIntegerField(blank=False, null=False)
    timer_type_id = models.IntegerField(blank=False, null=False)   
    timer_datetime = models.DateTimeField(blank=False, null=False)
    comment = models.CharField(blank=True, max_length=1000)
    created_by_id = models.BigIntegerField()
    created_date = models.DateTimeField()
    hostility_type_id = models.IntegerField(blank=True, null=True)      
    structure_type_id = models.IntegerField(blank=True, null=True)
    structure_type = models.CharField(max_length=50)
    solar_system = models.CharField(max_length=50)
    timer_type_name = models.CharField(max_length=50)
    created_by = models.CharField(max_length=255)
    structure_id = models.BigIntegerField(blank=True, null=True)
    fleet_commander = models.CharField(blank=True, max_length=255, null=True)
    structure_name = models.CharField(blank=True, max_length=255, null=True)

    class Meta:
        managed = False              
        default_permissions = ()        
        db_table = "cm_corp_timer_view"


class StructureRegistryView(models.Model):
    structure_id = models.BigIntegerField(primary_key=True)
    structure_name = models.CharField(blank=False, null=False, max_length=1000)
    structure_type_id = models.IntegerField(blank=False, null=False)
    structure_type = models.CharField(blank=True, max_length=100)   
    solar_system_id = models.IntegerField(blank=False, null=False)
    solar_system = models.CharField(blank=True, max_length=100)
    constellation_id = models.IntegerField(blank=False, null=False)
    constellation = models.CharField(blank=True, max_length=100)
    region_id = models.IntegerField(blank=False, null=False)
    alliance_id = models.IntegerField(blank=False, null=False)
    alliance = models.CharField(blank=True, max_length=50)                     
    corporation_id = models.IntegerField(blank=False, null=False)
    corporation = models.CharField(blank=True, max_length=50)   
    fit_json = models.TextField(blank=True)
    fit_last_updated_date = models.DateTimeField(blank=True, null=True)
    fit_last_updated_by = models.CharField(blank=True, max_length=254)   
    vulnerability = models.CharField(blank=True, max_length=10, null=True)      
    timer_datetime = models.DateTimeField(blank=True, null=True)
    timer_type = models.CharField(blank=True, max_length=50, null=True)     
    removed_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False              
        default_permissions = ()        
        db_table = "cm_structure_registry_view"                               