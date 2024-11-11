from django import forms
from .models import Voter

class VoterFilterForm(forms.Form):
    party = forms.ChoiceField(
        choices=[('', 'Any')] + [(pa, pa) for pa in Voter.objects.values_list('party_affiliation', flat=True).distinct()],
        required=False,
        label="Party Affiliation"
    )
    min_birth_year = forms.ChoiceField(
        choices=[('', 'Any')] + [(str(y), str(y)) for y in range(1913, 2024)],
        required=False,
        label="Minimum Birth Year"
    )
    max_birth_year = forms.ChoiceField(
        choices=[('', 'Any')] + [(str(y), str(y)) for y in range(1913, 2024)],
        required=False,
        label="Maximum Birth Year"
    )
    voter_score = forms.ChoiceField(
        choices=[('', 'Any')] + [(str(score), str(score)) for score in range(0, 6)],
        required=False,
        label="Voter Score"
    )
    # Election checkboxes
    v20state = forms.BooleanField(required=False, label="2020 State Election")
    v21town = forms.BooleanField(required=False, label="2021 Town Election")
    v21primary = forms.BooleanField(required=False, label="2021 Primary Election")
    v22general = forms.BooleanField(required=False, label="2022 General Election")
    v23town = forms.BooleanField(required=False, label="2023 Town Election")