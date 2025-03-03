"""Routes."""

from django.urls import path

from . import views

app_name = "cmStructureRegistry"

urlpatterns = [
    path("", views.index, name="index"),
    path("Timers", views.timers, name="timers"),
    path("GetOpenTimers", views.get_open_timers),
    path("GetRecentTimers", views.get_recent_timers),
    path("GetTimer", views.get_timer),               
    path("GetTimerTypes", views.timer_types),
    path("GetStructureTypes", views.structure_types),   
    path("GetHostilityTypes", views.timer_hostility_types),
    path("SearchRegions", views.search_regions),       
    path("SearchSolarSystems", views.search_solar_systems),
    path("GetPlanets", views.get_planets),
    path("AddTimer", views.save_timer),
    path("DeleteTimer", views.delete_timer),    
    path("SetFleetCommander", views.set_fleetcommander),
    path("SearchRegistry", views.search_registry),
    path("RegistryRead", views.registry_read),
    path("GetStructure", views.get_structure),
    path("SaveStructure", views.save_structure),
    path("AddStructureFit", views.save_structure_fit),
    path("SaveStructureVulnerability", views.save_structure_vuln),
    path("RemoveStructure", views.delete_structure),
    path("SearchUniverse", views.search_universe),
    path("SearchCorps", views.search_corps),
    path("SearchStructure", views.search_structure)
]
