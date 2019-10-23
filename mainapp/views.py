from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import View

from mainapp.models import Character, Campaign, Location, Lore, KnownLoreCharacter, Session, CharacterSession


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

        gm_char = Character(name='Game Master', campaign=campaign, user=user, description="The one and only",
                            image="images/dm.jpg")
        gm_char.save()

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        try:
            gm_char.known_characters.set(*all_chars)
        except Exception:
            pass

        for lore in all_lores:
            if not KnownLoreCharacter.objects.filter(character=gm_char, lore=lore).exists():
                KnownLoreCharacter.objects.create(character=gm_char, lore=lore, level=4)

        try:
            gm_char.known_locations.set(*all_locations)
        except Exception:
            pass

        gm_char.save()

        campaign.players.add(user)
        campaign.save()

        return response


class SessionCreateView(CreateView):
    model = Session
    template_name = 'new-session.html'
    fields = ['order', 'description', 'game_master_log']

    def form_valid(self, form):
        session = form.save(commit=False)
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        session.campaign = campaign
        session.save()

        for char in list(Character.objects.filter(campaign=campaign)):
            CharacterSession.objects.create(character=char, session=session)

        return redirect('session-profile', pk=self.kwargs['pk'], sessionid=session.id)


class SessionProfileView(DetailView):
    model = Session
    template_name = 'session.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        context = super(SessionProfileView, self).get_context_data(**kwargs)
        session_id = self.kwargs['sessionid']
        session = Session.objects.get(id=session_id)
        context['campaign'] = campaign
        context['character_sessions'] = CharacterSession.objects.filter(session=session)

        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(SessionProfileView, self).dispatch(*args, **kwargs)


class SessionsView(ListView):
    model = Session
    template_name = 'sessions.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        sessions = Session.objects.filter(campaign=campaign).order_by('order')

        return sessions

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(SessionsView, self).dispatch(*args, **kwargs)


class CharacterCreateView(CreateView):
    model = Character
    template_name = 'new-character.html'
    fields = ['name', 'image', 'description', 'user', 'known_characters', 'known_locations', 'own_lore', 'known_lores']

    def form_valid(self, form):
        char = form.save(commit=False)
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        char.campaign = campaign
        char.save()

        for lore in list(form.cleaned_data['known_lores']):
            KnownLoreCharacter.objects.create(character=char, lore=lore, level=1)

        if char.own_lore:
            KnownLoreCharacter.objects.create(character=char, lore=char.own_lore, level=4)

        gm_char = Character.objects.get(campaign=campaign, name='Game Master')

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))
        gm_char.known_characters.add(*all_chars)

        for lore in all_lores:
            if not KnownLoreCharacter.objects.filter(character=gm_char, lore=lore).exists():
                KnownLoreCharacter.objects.create(character=gm_char, lore=lore, level=4)

        gm_char.known_locations.add(*all_locations)

        return redirect('known-characters', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(CharacterCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        context['form'].fields['known_characters'].queryset = Character.objects.filter(campaign=campaign)
        context['form'].fields['known_lores'].queryset = Lore.objects.filter(campaign=campaign)
        context['form'].fields['known_locations'].queryset = Location.objects.filter(campaign=campaign)
        context['form'].fields['own_lore'].queryset = Lore.objects.filter(campaign=campaign)

        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharacterCreateView, self).dispatch(*args, **kwargs)


class LocationCreateView(CreateView):
    model = Location
    template_name = 'new-location.html'
    fields = ['name', 'description', 'important_characters', 'parent_location', 'own_lore']

    def form_valid(self, form):
        location = form.instance
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        location.campaign = campaign
        location.save()

        gm_char = Character.objects.get(campaign=campaign, name='Game Master')

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        gm_char.known_characters.add(*all_chars)

        for lore in all_lores:
            if not KnownLoreCharacter.objects.filter(character=gm_char, lore=lore).exists():
                KnownLoreCharacter.objects.create(character=gm_char, lore=lore, level=4)

        gm_char.known_locations.add(*all_locations)
        gm_char.save()

        return redirect('known-locations', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LocationCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign
        context['form'].fields['important_characters'].queryset = Character.objects.filter(campaign=campaign)
        context['form'].fields['parent_location'].queryset = Location.objects.filter(campaign=campaign)
        context['form'].fields['own_lore'].queryset = Lore.objects.filter(campaign=campaign)

        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationCreateView, self).dispatch(*args, **kwargs)


class LoreCreateView(CreateView):
    model = Lore
    template_name = 'new-lore.html'
    fields = ['type', 'title', 'text_level1', 'text_level2', 'text_level3', 'text_level4']

    def form_valid(self, form):
        lore = form.instance
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        lore.campaign = campaign
        lore.save()

        gm = campaign.game_master
        gm_char = Character.objects.get(user=gm)

        all_chars = list(Character.objects.filter(campaign=campaign))
        all_locations = list(Location.objects.filter(campaign=campaign))
        all_lores = list(Lore.objects.filter(campaign=campaign))

        gm_char.known_characters.add(*all_chars)

        for lore in all_lores:
            if not KnownLoreCharacter.objects.filter(character=gm_char, lore=lore).exists():
                KnownLoreCharacter.objects.create(character=gm_char, lore=lore, level=4)

        gm_char.known_locations.add(*all_locations)
        gm_char.save()

        return redirect('known-lores', pk=self.kwargs['pk'], charid=self.kwargs['charid'])

    def get_context_data(self, **kwargs):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        context = super(LoreCreateView, self).get_context_data(**kwargs)

        context['campaign'] = campaign

        return context

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoreCreateView, self).dispatch(*args, **kwargs)


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
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        locations = list(Location.objects.filter(parent_location__isnull=True, campaign=campaign))

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


class KnownCharacterRemoveView(View):

    def post(self, request, **kwargs):
        current_char_id = self.kwargs['knowncharid']
        to_remove_char_id = self.kwargs['toremovecharid']

        current_char = Character.objects.get(id=current_char_id)
        current_char.known_characters.remove(Character.objects.get(id=to_remove_char_id))
        current_char.save()

        return redirect('character-profile', pk=self.kwargs['pk'], charid=self.kwargs['charid'],
                        knowncharid=self.kwargs['knowncharid'])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownCharacterRemoveView, self).dispatch(*args, **kwargs)


class KnownLoreRemoveView(View):

    def post(self, request, **kwargs):
        current_char_id = self.kwargs['knowncharid']
        to_remove_lore_id = self.kwargs['toremoveloreid']

        current_char = Character.objects.get(id=current_char_id)
        to_remove_knownlorechar = KnownLoreCharacter.objects.get(character=current_char_id, lore=to_remove_lore_id)
        to_remove_knownlorechar.delete()
        current_char.save()

        return redirect('character-profile', pk=self.kwargs['pk'], charid=self.kwargs['charid'],
                        knowncharid=self.kwargs['knowncharid'])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLoreRemoveView, self).dispatch(*args, **kwargs)


class KnownCharacterAddView(View):

    def post(self, request, **kwargs):
        current_char_id = self.kwargs['knowncharid']
        to_add_char_id = self.kwargs['toaddcharid']

        current_char = Character.objects.get(id=current_char_id)
        current_char.known_characters.add(Character.objects.get(id=to_add_char_id))
        current_char.save()

        return redirect('character-profile', pk=self.kwargs['pk'], charid=self.kwargs['charid'],
                        knowncharid=self.kwargs['knowncharid'])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownCharacterAddView, self).dispatch(*args, **kwargs)


class KnownLoreAddView(View):

    def post(self, request, **kwargs):
        current_char_id = self.kwargs['knowncharid']
        to_add_lore_id = self.kwargs['toaddloreid']

        current_char = Character.objects.get(id=current_char_id)
        if not KnownLoreCharacter.objects.filter(character=current_char, lore=to_add_lore_id).exists():
            KnownLoreCharacter.objects.create(character=current_char, lore=Lore.objects.get(id=to_add_lore_id))

        return redirect('character-profile', pk=self.kwargs['pk'], charid=self.kwargs['charid'],
                        knowncharid=self.kwargs['knowncharid'])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(KnownLoreAddView, self).dispatch(*args, **kwargs)


class UpdateKnownLoreLevelView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateKnownLoreLevelView, self).dispatch(request, *args, **kwargs)

    def post(self, request, **kwargs):
        level = self.kwargs['level']
        knownloreid = self.kwargs['knownloreid']

        knownlore = KnownLoreCharacter.objects.get(id=knownloreid)
        knownlore.level = level
        knownlore.save()

        messages.success(request, 'Lore level updated for the character')
        return JsonResponse({'success': True})

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(UpdateKnownLoreLevelView, self).dispatch(*args, **kwargs)


class CharacterProfileView(View):
    template_name = 'character.html'

    def get(self, request, **kwargs):
        char_id = self.kwargs['charid']
        known_char_id = self.kwargs['knowncharid']
        char = Character.objects.get(id=char_id)
        known_char = Character.objects.get(id=known_char_id)

        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        knownlores = KnownLoreCharacter.objects.filter(character=known_char_id)
        try:
            own_lore_knownlore = KnownLoreCharacter.objects.get(character=char_id, lore=known_char.own_lore.id)
        except Exception:
            own_lore_knownlore = None

        knownlorelevels = list()
        if own_lore_knownlore:
            for i in range(1, own_lore_knownlore.level + 1):
                knownlorelevels.append(own_lore_knownlore.lore.text_of_level(i))
        else:
            knownlorelevels.append(
                "The old librarian comes back to tell you that he couldn't find anything useful on this character")

        context = dict()
        context['campaign'] = campaign
        context['character'] = known_char
        context['current_char'] = char
        context['knownlores'] = knownlores
        context['own_lore_knownlore'] = knownlorelevels
        return render(request, self.template_name, context)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharacterProfileView, self).dispatch(*args, **kwargs)


class CharacterUpdateView(UpdateView):
    template_name = 'character-update.html'
    model = Character
    fields = ['name', 'image', 'description', 'user', 'own_lore']

    def get_context_data(self, **kwargs):
        context = super(CharacterUpdateView, self).get_context_data(**kwargs)
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        context['campaign'] = campaign
        return context

    def get_object(self, queryset=None):
        char_id = self.kwargs['knowncharid']
        character = Character.objects.get(id=char_id)
        return character

    def get_success_url(self):
        return reverse('character-profile', args=[self.kwargs['pk'], self.kwargs['charid'],
                                                  self.kwargs['knowncharid']])

    def form_valid(self, form):
        char = form.save()
        if char.own_lore:
            KnownLoreCharacter.objects.create(character=char, lore=char.own_lore, level=4)
        return super().form_valid(form)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(CharacterUpdateView, self).dispatch(*args, **kwargs)


class LoreProfileView(View):
    model = Character
    template_name = 'lore.html'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoreProfileView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        lore_id = self.kwargs['loreid']
        lore = Lore.objects.get(id=lore_id)

        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        char_id = self.kwargs['charid']
        char = Character.objects.get(id=char_id)

        context = dict()
        context['campaign'] = campaign
        context['lore'] = lore
        context['character'] = char

        if 'charid' in self.kwargs:
            char_id = self.kwargs['charid']
            char = Character.objects.get(id=char_id)
            knownlore = KnownLoreCharacter.objects.get(character=char, lore=lore)
            knownlorelevels = list()
            for i in range(1, knownlore.level + 1):
                knownlorelevels.append(lore.text_of_level(i))

            context['knownlore'] = knownlorelevels

        return render(request, self.template_name, context)


class LoreUpdateView(UpdateView):
    template_name = 'lore-update.html'
    model = Lore
    fields = ['type', 'title', 'text_level1', 'text_level2', 'text_level3', 'text_level4']

    def get_context_data(self, **kwargs):
        context = super(LoreUpdateView, self).get_context_data(**kwargs)
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        context['campaign'] = campaign
        return context

    def get_object(self, queryset=None):
        lore_id = self.kwargs['loreid']
        lore = Lore.objects.get(id=lore_id)
        return lore

    def get_success_url(self):
        return reverse('lore-profile', args=[self.kwargs['pk'], self.kwargs['charid'],
                                             self.kwargs['loreid']])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LoreUpdateView, self).dispatch(*args, **kwargs)


class LocationProfileView(View):
    model = Location
    template_name = 'location.html'

    def get(self, request, **kwargs):
        loc_id = self.kwargs['locationid']
        location = Location.objects.get(id=loc_id)

        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        char_id = self.kwargs['charid']
        char = Character.objects.get(id=char_id)

        try:
            own_lore_knownlore = KnownLoreCharacter.objects.get(character=char_id, lore=location.own_lore.id)
        except Exception:
            own_lore_knownlore = None

        knownlorelevels = list()

        if own_lore_knownlore:
            for i in range(1, own_lore_knownlore.level + 1):
                knownlorelevels.append(own_lore_knownlore.lore.text_of_level(i))
        else:
            knownlorelevels.append(
                "The old librarian comes back to tell you that he couldn't find anything useful on this character")

        context = dict()
        context['campaign'] = campaign
        context['location'] = location
        context['character'] = char
        context['own_lore_knownlore'] = knownlorelevels
        return render(request, self.template_name, context)

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationProfileView, self).dispatch(*args, **kwargs)


class LocationUpdateView(UpdateView):
    template_name = 'location-update.html'
    model = Location
    fields = ['name', 'parent_location', 'description', 'important_characters', 'own_lore']

    def get_context_data(self, **kwargs):
        context = super(LocationUpdateView, self).get_context_data(**kwargs)
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        context['campaign'] = campaign
        return context

    def get_object(self, queryset=None):
        location_id = self.kwargs['locationid']
        location = Location.objects.get(id=location_id)
        return location

    def get_success_url(self):
        return reverse('location-profile', args=[self.kwargs['pk'], self.kwargs['charid'],
                                                 self.kwargs['locationid']])

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(LocationUpdateView, self).dispatch(*args, **kwargs)


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
