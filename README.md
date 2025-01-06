# Structure Registry and Timer Board

This is a Structure Registry and Timer Board app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) (AA) 

## Features

- Structure Registry with ability to paste in fit information, set windows and add timer with stucture auto-populated
- Structure Registry will show if a timer is linked to structure and remaining time
- Timer Board with open and recent timers with ability to set Lead FC
- Automatic count up after countdown based on structure type
- When adding Timer, one can search Structure Registry 
- Add a Timer based on EVE reinforce text from a structure

## Installation

Once you have cloned the repo or copied all files into place.

Make sure you are in your venv. Then install it with pip in editable mode:

```bash
pip install -e {path_to}/cmStructureRegistry
```

First add your app to the Django project by adding 'cmStructureRegistry' to INSTALLED_APPS in `settings/local.py`.

Next make migrations for the app:

```bash
python manage.py makemigrations
```

Then run a check to see if everything is setup correctly.

```bash
python manage.py check
```

In case they are errors make sure to fix them before proceeding.

Next perform migrations to add your model to the database:

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

View Structure Registry menu item and view and search Structure Registry page:
    cmStructureRegistry.view_structureregistry

Add or modify a structure:
    cmStructureRegistry.add_structureregistry

Add or change a structure fit on a structure:
    cmStructureRegistry.change_structureregistry    

Set structure vulnerability window:
    cmStructureRegistry.change_structureregistry    

Remove a structure:
    cmStructureRegistry.delete_structureregistry    

View Timer menu item and Timer page:
    cmStructureRegistry.view_corptimer

Add Timer:
    cmStructureRegistry.add_corptimer

Set Fleet Commander:
    cmStructureRegistry.change_corptimer

Remove Timer:
    cmStructureRegistry.delete_corptimer












