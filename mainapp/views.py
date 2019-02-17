from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import View

from mainapp.models import Character, Campaign, Location, Lore


# home

class CharactersView(ListView):
    model = Character
    template_name = 'characters.html'
    context_object_name = 'characters'

    def get_queryset(self):
        user = self.request.user
        characters = Character.objects.filter(user=user)
        return characters

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharactersView, self).dispatch(*args, **kwargs)


class CampaignsView(ListView):
    model = Campaign
    template_name = 'campaigns.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        user = self.request.user
        campaigns = Campaign.objects.filter(players=user)
        return campaigns

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CampaignsView, self).dispatch(*args, **kwargs)


# dm creates

class CampaignCreateView(CreateView):
    model = Campaign
    template_name = 'new-campaign.html'
    fields = '__all__'

    def form_valid(self, form):
        response = super(CampaignCreateView, self).form_valid(form)
        self.object = form.save()
        id = self.object.id
        campaign = Campaign.objects.get(id=id)
        user = campaign.game_master
        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        gm_char = Character(name='Game Master', campaign=campaign, user=user)
        gm_char.save()

        gm_char.known_characters.set(*all_chars)
        gm_char.known_lores.set(*all_lores)
        gm_char.known_locations.set(*all_locations)
        gm_char.save()

        campaign.players.add(user)
        campaign.save()

        return response


class CharacterCreateView(CreateView):
    model = Character
    template_name = 'new-character.html'
    fields = '__all__'

    def form_valid(self, form):
        form.save()
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        gm_char = Character.objects.get(campaign=campaign, name='Game Master')

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))
        gm_char.known_characters.add(*all_chars)
        gm_char.known_lores.add(*all_lores)
        gm_char.known_locations.add(*all_locations)

        return redirect('known-characters', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CharacterCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context


class LocationCreateView(CreateView):
    model = Location
    template_name = 'new-location.html'
    fields = '__all__'

    def form_valid(self, form):
        form.save()
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        gm_char = Character.objects.get(campaign=campaign, name='Game Master')

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        gm_char.known_characters.add(*all_chars)
        gm_char.known_lores.add(*all_lores)
        gm_char.known_locations.add(*all_locations)
        gm_char.save()

        return redirect('known-locations', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LocationCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context


class LoreCreateView(CreateView):
    model = Lore
    template_name = 'new-lore.html'
    fields = '__all__'

    def form_valid(self, form):
        form.save()
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        gm = campaign.game_master
        gm_char = Character.objects.get(user=gm)

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        gm_char.known_characters.set(*all_chars)
        gm_char.known_lores.set(*all_lores)
        gm_char.known_locations.set(*all_locations)
        gm_char.save()

        return redirect('known-lores', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LoreCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context


# campaign page


class CampaignProfileView(DetailView):
    model = Campaign
    template_name = 'campaign-home.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CampaignProfileView, self).get_context_data(**kwargs)
        if 'charid' in self.kwargs:
            char_id = self.kwargs['charid']
            char = Character.objects.get(id=char_id)
            context['character'] = char
        elif self.request.user == campaign.game_master:
            gm_char = Character.objects.get(campaign=campaign, name='Game Master')
            context['character'] = gm_char
        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CampaignProfileView, self).dispatch(*args, **kwargs)


class CampaignUpdateView(UpdateView):
    model = Campaign
    template_name = 'campaign-update.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CampaignUpdateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CampaignUpdateView, self).dispatch(*args, **kwargs)


class MyCharactersView(ListView):
    model = Character
    template_name = 'characters.html'
    context_object_name = 'characters'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(MyCharactersView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        characters = Character.objects.filter(campaign=campaign, user=self.request.user)
        return characters

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(MyCharactersView, self).dispatch(*args, **kwargs)


class CampaignCharactersView(ListView):
    model = Character
    template_name = 'campaign-characters.html'
    context_object_name = 'characters'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CampaignCharactersView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        characters = Character.objects.filter(campaign=campaign)
        return characters

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CampaignCharactersView, self).dispatch(*args, **kwargs)


class KnownLoresView(ListView):
    model = Lore
    template_name = 'lores.html'
    context_object_name = 'lores'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(KnownLoresView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    def get_queryset(self):
        char_id = self.kwargs['charid']
        char = Character.objects.get(id=char_id)
        return char.known_lores.all

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLoresView, self).dispatch(*args, **kwargs)


class KnownLocationsView(ListView):
    model = Location
    template_name = 'locations.html'
    context_object_name = 'locations'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(KnownLocationsView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    def get_queryset(self):
        locations = list(Location.objects.filter(parent_location__isnull=True))

        return locations

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLocationsView, self).dispatch(*args, **kwargs)


class KnownCharactersView(ListView):
    model = Character
    template_name = 'known-characters.html'
    context_object_name = 'characters'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(KnownCharactersView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        return context

    def get_queryset(self):
        char_id = self.kwargs['charid']
        char = Character.objects.get(id=char_id)
        return char.known_characters.all

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownCharactersView, self).dispatch(*args, **kwargs)


# campaign model profiles
# todo filter knowledge

class CharacterProfileView(View):
    template_name = 'character.html'

    def get(self, request, **kwargs):
        char_id = self.kwargs['charid']
        known_char_id = self.kwargs['knowncharid']
        char = Character.objects.get(id=char_id)
        known_char = Character.objects.get(id=known_char_id)

        context = dict()
        context['character'] = known_char

        return render(request, self.template_name, context)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharacterProfileView, self).dispatch(*args, **kwargs)


class LoreProfileView(View):
    model = Character
    template_name = 'lore.html'

    def get(self, request, **kwargs):
        lore_id = self.kwargs['loreid']
        lore = Lore.objects.get(id=lore_id)

        context = dict()
        context['lore'] = lore

        return render(request, self.template_name, context)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoreProfileView, self).dispatch(*args, **kwargs)


class LocationProfileView(View):
    model = Location
    template_name = 'location.html'

    def get(self, request, **kwargs):
        loc_id = self.kwargs['locationid']
        location = Location.objects.get(id=loc_id)

        context = dict()
        context['location'] = location

        return render(request, self.template_name, context)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationProfileView, self).dispatch(*args, **kwargs)


class NavLoader(View):
    template_name = 'campaign-nav.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NavLoader, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = dict()

        context['campaign'] = campaign
        if 'charid' in self.kwargs:
            char_id = self.kwargs['charid']
            char = Character.objects.get(id=char_id)
            context['character'] = char
        elif self.request.user == campaign.game_master:
            gm_char = Character.objects.get(campaign=campaign, name='Game Master')
            context['character'] = gm_char

        return render(request, self.template_name, context)
