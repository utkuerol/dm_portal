from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, CreateView, UpdateView

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
        all_chars = Character.objects.filter(campaign=campaign)
        all_locations = Location.objects.filter(campaign=campaign)
        all_lores = Lore.objects.filter(campaign=campaign)

        gm_char = Character(name='Game Master', campaign=campaign, user=user)
        gm_char.save()

        gm_char.known_characters.set(all_chars)
        gm_char.known_lores.set(all_lores)
        gm_char.known_locations.set(all_locations)
        gm_char.save()

        campaign.players.add(user)
        campaign.save()

        return response


class CharacterCreateView(CreateView):
    model = Character
    template_name = 'new-character.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CharacterCreateView, self).get_context_data(**kwargs)
        context['campaign'] = campaign
        if 'char-id' in kwargs:
            char_id = kwargs['char-id']
            char = Character.objects.get(id=char_id)
            context['character'] = char
        elif self.request.user == campaign.game_master:
            gm_char = Character.objects.get(campaign=campaign, name='Game Master')
            context['character'] = gm_char
        return context

class LocationCreateView(CreateView):
    model = Location
    template_name = 'new-location.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LocationCreateView, self).get_context_data(**kwargs)
        context['campaign'] = campaign
        if 'char-id' in kwargs:
            char_id = kwargs['char-id']
            char = Character.objects.get(id=char_id)
            context['character'] = char
        elif self.request.user == campaign.game_master:
            gm_char = Character.objects.get(campaign=campaign, name='Game Master')
            context['character'] = gm_char
        return context


class LoreCreateView(CreateView):
    model = Lore
    template_name = 'new-lore.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LoreCreateView, self).get_context_data(**kwargs)
        context['campaign'] = campaign
        if 'char-id' in kwargs:
            char_id = kwargs['char-id']
            char = Character.objects.get(id=char_id)
            context['character'] = char
        elif self.request.user == campaign.game_master:
            gm_char = Character.objects.get(campaign=campaign, name='Game Master')
            context['character'] = gm_char
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
        if 'char-id' in kwargs:
            char_id = kwargs['char-id']
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

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CampaignUpdateView, self).dispatch(*args, **kwargs)


class MyCharactersView(ListView):
    model = Character
    template_name = 'characters.html'
    context_object_name = 'characters'

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        characters = Character.objects.filter(campaign=campaign, user=self.request.user)
        return characters

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(MyCharactersView, self).dispatch(*args, **kwargs)


class LocationsView(ListView):
    model = Location
    template_name = 'locations.html'
    context_object_name = 'locations'

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        locations = Location.objects.filter(campaigns=campaign)
        return locations

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationsView, self).dispatch(*args, **kwargs)


class LoresView(ListView):
    model = Lore
    template_name = 'lores.html'
    context_object_name = 'lores'

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        lores = Lore.objects.filter(campaigns=campaign)
        return lores

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoresView, self).dispatch(*args, **kwargs)


class CampaignCharactersView(ListView):
    model = Character
    template_name = 'campaign-characters.html'
    context_object_name = 'characters'

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
    template_name = 'known-lores.html'
    context_object_name = 'lores'

    def get_queryset(self):
        char_id = self.request.GET.get('char_id')
        char = Character.objects.get(id=char_id)
        return char.known_lores

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLoresView, self).dispatch(*args, **kwargs)


class KnownLocationsView(ListView):
    model = Location
    template_name = 'known-locations.html'
    context_object_name = 'locations'

    def get_queryset(self):
        char_id = self.request.GET.get('char_id')
        char = Character.objects.get(id=char_id)
        return char.known_locations

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLocationsView, self).dispatch(*args, **kwargs)


class KnownCharactersView(ListView):
    model = Character
    template_name = 'known-characters.html'
    context_object_name = 'characters'

    def get_queryset(self):
        char_id = self.request.GET.get('char_id')
        char = Character.objects.get(id=char_id)
        return char.known_characters

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownCharactersView, self).dispatch(*args, **kwargs)


# campaign model profiles
# todo filter knowledge

class CharacterProfileView(DetailView):
    model = Character
    template_name = 'character.html'
    context_object_name = 'character'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharacterProfileView, self).dispatch(*args, **kwargs)


class LoreProfileView(DetailView):
    model = Character
    template_name = 'lore.html'
    context_object_name = 'lore'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoreProfileView, self).dispatch(*args, **kwargs)


class LocationProfileView(DetailView):
    model = Location
    template_name = 'location.html'
    context_object_name = 'location'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationProfileView, self).dispatch(*args, **kwargs)
