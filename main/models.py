import self as self
from django.contrib.auth.models import User
from django.db import models


class Campaign(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    users = models.ManyToManyField(User, related_name="players")
    game_master = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_master")


class Location(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    campaign = models.ManyToManyField(Campaign)
    important_characters = models.ManyToManyField("Character", blank=True)
    parent_location = models.ForeignKey("Location", on_delete=models.CASCADE, null=True, blank=True)
    own_lore = models.ForeignKey("Lore", on_delete=models.CASCADE, null=True)


class Character(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    image = models.ImageField(upload_to="images", null=True)
    description = models.CharField(max_length=10000, null=False)
    campaign = models.ManyToManyField(Campaign)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    known_characters = models.ManyToManyField("Character", blank=True)
    known_locations = models.ManyToManyField("Location", blank=True)
    own_lore = models.ForeignKey("Lore", on_delete=models.CASCADE, null=True, related_name="own_lore")
    known_lores = models.ManyToManyField("Lore", blank=True, related_name="known_lores")


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
