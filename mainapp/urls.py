from django.urls import path

from mainapp.views import CampaignsView, CharactersView, \
    CampaignCharactersView, KnownLoresView, KnownLocationsView, KnownCharactersView, CampaignProfileView, \
    LoreProfileView, LocationProfileView, CharacterProfileView, CampaignCreateView, CampaignUpdateView, \
    MyCharactersView, CharacterCreateView, LocationCreateView, LoreCreateView, NavLoader, KnownCharacterRemoveView, \
    KnownLoreRemoveView, KnownLoreAddView, KnownCharacterAddView, UpdateKnownLoreLevelView, CharacterUpdateView, \
    LocationUpdateView, LoreUpdateView, SessionCreateView, SessionProfileView, SessionsView, SessionUpdateView, \
    CharacterSessionUpdateView

urlpatterns = [
    path('campaigns/', CampaignsView.as_view(), name='campaigns'),
    path('characters/', CharactersView.as_view(), name='characters'),
    path('campaigns/new', CampaignCreateView.as_view(), name='new-campaign'),
    path('campaigns/<int:pk>/update', CampaignUpdateView.as_view(), name='campaign-update'),
    path('campaigns/<int:pk>/sessions/new', SessionCreateView.as_view(), name='new-session'),
    path('campaigns/<int:pk>/<int:charid>/sessions/<int:sessionid>', SessionProfileView.as_view(),
         name='session-profile'),
    path('campaigns/<int:pk>/<int:charid>/sessions/', SessionsView.as_view(), name='sessions'),
    path('campaigns/<int:pk>/<int:charid>/sessions/<int:sessionid>/update', SessionUpdateView.as_view(),
         name='session-update'),
    path('campaigns/<int:pk>/<int:charid>/sessions/<int:sessionid>/<int:charactersessionid>/update',
         CharacterSessionUpdateView.as_view(),
         name='character-session-update'),

    path('campaigns/<int:pk>', CampaignProfileView.as_view(), name='campaign-profile'),
    path('campaigns/<int:pk>/<int:charid>', CampaignProfileView.as_view(), name='campaign-character-profile'),
    path('campaigns/<int:pk>/characters/', MyCharactersView.as_view(), name='my-characters'),
    path('campaigns/<int:pk>/<int:charid>/characters/', CampaignCharactersView.as_view(), name='campaign-characters'),
    path('campaigns/<int:pk>/<int:charid>/known-locations', KnownLocationsView.as_view(), name='known-locations'),
    path('campaigns/<int:pk>/<int:charid>/known-lores/', KnownLoresView.as_view(), name='known-lores'),
    path('campaigns/<int:pk>/<int:charid>/known-characters/', KnownCharactersView.as_view(), name='known-characters'),
    path('campaigns/<int:pk>/<int:charid>/lores/<int:loreid>', LoreProfileView.as_view(), name='lore-profile'),
    path('campaigns/<int:pk>/<int:charid>/lores/<int:loreid>/update', LoreUpdateView.as_view(), name='lore-update'),
    path('campaigns/<int:pk>/<int:charid>/locations/<int:locationid>', LocationProfileView.as_view(),
         name='location-profile'),
    path('campaigns/<int:pk>/<int:charid>/locations/<int:locationid>/update', LocationUpdateView.as_view(),
         name='location-update'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>', CharacterProfileView.as_view(),
         name='character-profile'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>/update', CharacterUpdateView.as_view(),
         name='character-update'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>/removeknownchar/<int:toremovecharid>',
         KnownCharacterRemoveView.as_view(),
         name='known-character-remove'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>/addknownchar/<int:toaddcharid>',
         KnownCharacterAddView.as_view(),
         name='add-known-char'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>/removeknownlore/<int:toremoveloreid>',
         KnownLoreRemoveView.as_view(),
         name='known-lore-remove'),
    path('campaigns/<int:pk>/<int:charid>/characters/<int:knowncharid>/addknownlore/<int:toaddloreid>',
         KnownLoreAddView.as_view(),
         name='add-known-lore'),
    path('campaigns/<int:pk>/<int:charid>/characters/new', CharacterCreateView.as_view(), name='new-character'),
    path('campaigns/<int:pk>/<int:charid>/locations/new', LocationCreateView.as_view(), name='new-location'),
    path('campaigns/<int:pk>/<int:charid>/lore/new', LoreCreateView.as_view(), name='new-lore'),

    path('campaigns/<int:pk>/loadnav', NavLoader.as_view(), name='loadnav'),
    path('campaigns/<int:pk>/<int:charid>/loadnav', NavLoader.as_view(), name='loadnav-with-char'),

    path('update-knownlore-level/<int:level>/<int:knownloreid>', UpdateKnownLoreLevelView.as_view(),
         name='update-knownlore-level'),
]
