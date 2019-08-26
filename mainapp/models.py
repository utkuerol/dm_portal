import self as self
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Setting(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    players = models.ManyToManyField(User, related_name="players", blank=True)
    game_master = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="game_master")
    setting = models.ForeignKey(Setting, on_delete=models.SET_NULL, related_name="setting", null=True, blank=True)

    def get_absolute_url(self):
        return reverse('campaign-profile', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    campaign = models.ManyToManyField(Campaign)
    important_characters = models.ManyToManyField("Character", blank=True)
    parent_location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True)
    own_lore = models.ForeignKey("Lore", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def get_children(self):
        children = list()
        locations = Location.objects.all()
        for location in locations:
            if location in list(Location.objects.filter(parent_location=self)):
                children.append(location)
        return children


class Character(models.Model):
    name = models.CharField(max_length=100, null=False, unique=False)
    image = models.ImageField(upload_to="media", null=True, default="images/default_char.jpg")
    description = models.CharField(max_length=10000, blank=True)
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    known_characters = models.ManyToManyField("Character", blank=True)
    known_locations = models.ManyToManyField("Location", blank=True)
    own_lore = models.ForeignKey("Lore", on_delete=models.SET_NULL, null=True, blank=True, related_name="own_lore")
    known_lores = models.ManyToManyField("Lore", null=True, blank=True, related_name="known_lores", through="KnownLoreCharacter")

    def __str__(self):
        return self.name



LORE_TYPES = (
    ("HISTORY", "History"),
    ("ARCANE", "Arcane"),
    ("LOC", "Location"),
    ("CHAR", "Character")
)


class Lore(models.Model):
    campaign = models.ManyToManyField(Campaign)
    type = models.CharField(max_length=100, null=False, choices=LORE_TYPES)
    title = models.CharField(max_length=100, null=False, unique=True)
    text_level1 = models.TextField(blank=True, null=True)
    text_level2 = models.TextField(blank=True, null=True)
    text_level3 = models.TextField(blank=True, null=True)
    text_level4 = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def text_of_level(self, level):
        if level == 1:
            return self.text_level1
        elif level == 2:
            return self.text_level2
        elif level == 3:
            return self.text_level3
        elif level == 4:
            return self.text_level4
        else:
            return "Something doesn't seem right on the server :("

class KnownLoreCharacter(models.Model):
    character = models.ForeignKey("Character", on_delete=models.CASCADE)
    lore = models.ForeignKey("Lore", on_delete=models.CASCADE)
    level = models.IntegerField(default=1,
                                null=False, unique=False)
