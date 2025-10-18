# Structure Registry and Timer Board

This is a Structure Registry and Timer Board app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) (AA) 

## Features

- Structure Registry with ability to paste in fit information, set windows and add timer with stucture auto-populated
- Structure Registry will show if a timer is linked to structure and the remaining time
- Timer Board with open and recent timers with ability to set Lead FC
- Link from Timer to structure in Structure Registry if linked.
- Automatic count up after countdown based on structure type
- When adding Timer, one can search Structure Registry 
- Add a Timer based on EVE reinforce text from a structure
- Different timer access levels, Public (default), Skirmish, Tactical
- Optional background task to create friendly timers (requires corptools and importing of notifications)

## Installation

Once you have cloned the repo or copied all files into place.

Make sure you are in your venv. Then install it with pip in editable mode:

```bash
pip install -e {path_to}/cmStructureRegistry
```

First add your app to the Django project by adding 'cmStructureRegistry' to INSTALLED_APPS in `settings/local.py`.

Next perform migrations to add models to the database:

```bash
python manage.py migrate
```

Next initialize all the lookup data.

```bash
python manage.py loaddata cmStructureRegistry/init
```

Next initalize all the universe data such as regions, constellations and solar systems

```bash
python manage.py populate_universe
```

Next copy all the static data to the output folder

```bash
python manage.py collectstatic --noinput
```

Finally restart your AA setup.

## Permissions

There are two separate menu items in this plugin. One is for the Structure Registry and one is for Timers.

Here are the features of the plugin and what permissions allow them

View Structure Registry and Timers menu items
    *cmStructureRegistry.basic_access*

Add, modify a structure, fit or vulnerability:
    *cmStructureRegistry.manage_structures*

Remove a structure:
    *cmStructureRegistry.delete_structure*

Add Timer and set FCs:
    *cmStructureRegistry.manage_timers*

Remove Timer:
    *cmStructureRegistry.delete_timer*

View and Add Skirmish Level Timers (requires manage_timers permission):
    *cmStructureRegistry.skirmish_timer*

View and Add Tactical Level Timers (requires manage_timers permission):
    *cmStructureRegistry.tactical_timer*

## Friendly Timers

There is an optional feature that requires the corptools dependency.  It queries notifications and creates friendly timers.

To enable, create an Alliance Auth periodic task that runs the shared task: *cmStructureRegistry.tasks.notification_timer_task*









