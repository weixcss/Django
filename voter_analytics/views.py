from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from .forms import VoterFilterForm
import plotly.express as px
import pandas as pd

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100  

    def get_queryset(self):
        queryset = Voter.objects.all()

        # Get filter parameters from GET request
        party_affiliation = self.request.GET.get('party')
        min_birth_year = self.request.GET.get('min_birth_year')
        max_birth_year = self.request.GET.get('max_birth_year')
        voter_score = self.request.GET.get('voter_score')
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        # Apply filters if they are present in GET request
        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        if min_birth_year:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_birth_year))
        if max_birth_year:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_birth_year))
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))

        for election in elections:
            if self.request.GET.get(election) == 'on':
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = VoterFilterForm(self.request.GET or None)
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_detail.html'
    context_object_name = 'voter'

class GraphsView(ListView):
    template_name = 'graphs.html'
    model = Voter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Data for Year of Birth Histogram
        voters = Voter.objects.values('date_of_birth')
        df_birth_year = pd.DataFrame(voters)
        df_birth_year['year_of_birth'] = pd.to_datetime(df_birth_year['date_of_birth']).dt.year
        fig_birth_year = px.histogram(df_birth_year, x='year_of_birth', nbins=100, title="Voter distribution by Year of Birth")
        fig_birth_year.update_layout(xaxis_title="Year of Birth", yaxis_title="Number of Voters", title_x=0.5)
        context['voter_birth_year_histogram'] = fig_birth_year.to_html(full_html=False)

        # Data for Party Affiliation Pie Chart with adjustments
        voters_party = Voter.objects.values('party_affiliation')
        df_party = pd.DataFrame(voters_party)
        fig_party_affiliation = px.pie(
            df_party,
            names='party_affiliation',
            title="Voter distribution by Party Affiliation",
            hole=0.3
        )
        fig_party_affiliation.update_traces(textinfo='percent+label', pull=[0.1 if pa == "D" else 0 for pa in df_party['party_affiliation']])
        fig_party_affiliation.update_layout(
            title_x=0.5,
            height=800,  # Increase chart height for better visibility
            width=1000,  # Increase chart width
            margin=dict(t=50, l=50, r=200, b=50),  # Adjust margins to fit legend
            legend=dict(
                orientation="v",  # Set legend to vertical orientation
                yanchor="top",
                y=0.5,
                xanchor="right",
                x=1.3,  # Position the legend outside the chart area
                font=dict(size=12)
            )
        )
        context['voter_party_affiliation_pie'] = fig_party_affiliation.to_html(full_html=False)

        # Data for Election Participation Histogram
        voters_election = Voter.objects.values('v20state', 'v21town', 'v21primary', 'v22general', 'v23town')
        df_election = pd.DataFrame(voters_election)
        participation_counts = df_election.apply(pd.Series.value_counts).loc[True]
        fig_election = px.bar(
            x=participation_counts.index,
            y=participation_counts.values,
            title="Vote Count by Election",
            labels={'x': 'Election', 'y': 'Number of Voters'}
        )
        fig_election.update_layout(title_x=0.5)
        context['voter_election_histogram'] = fig_election.to_html(full_html=False)

        return context