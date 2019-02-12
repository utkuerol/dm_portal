import self as self
from django.contrib.auth.models import User
from django.db import models


class Campaign(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    users = models.ManyToManyField(User)
    game_master = models.ForeignKey(User, on_delete=models.CASCADE)


class Location(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    campaign = models.ManyToManyField(Campaign)
    important_characters = models.ManyToManyField("Character")
    parent_location = models.ForeignKey("Location", on_delete=models.CASCADE, null=True)


class Character(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    campaign = models.ManyToManyField(Campaign)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    known_characters = models.ManyToManyField(self)
    known_locations = models.ManyToManyField("Location")
