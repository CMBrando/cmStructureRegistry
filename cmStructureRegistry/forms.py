"""Forms."""

from django import forms
from .models import CorpTimer
from .models import StructureRegistry

class CorpTimerForm(forms.ModelForm):
    class Meta:
        model = CorpTimer
        fields = ['system_id', 'timer_type_id', 'timer_datetime', 'comment', 'structure_type_id', 'hostility_type_id', 'structure_type_id', 'structure_id', 'fleet_commander', 'planet']
        error_messages = {
            'system_id': {
                'required': 'System is required'
            },
            'timer_type_id': {
                'required': 'Timer Type is required'
            },
            'timer_datetime': {
                'required': 'Timer Date/Time or Countdown is required'
            }
        }


class FleetCommanderForm(forms.ModelForm):
    class Meta:
        model = CorpTimer
        fields = ['id', 'fleet_commander']

class StructureRegistryForm(forms.ModelForm):
 
    structure_id = forms.IntegerField(required=False)
    corporation_name = forms.CharField(max_length=255, required=True, error_messages = { 'required': 'Corporation Name is required' })

    class Meta:
        model = StructureRegistry
        fields = ['structure_name', 'structure_type_id']
        error_messages = {
            'structure_name': {
                'required': 'Structure Name is required'
            },
            'structure_type_id': {
                'required': 'Structure Type is required'
            }            
        }         