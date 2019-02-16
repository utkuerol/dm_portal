from django.contrib import admin

# Register your models here.
from mainapp.models import Campaign, Character, Lore, Location

admin.site.register(Campaign)
admin.site.register(Character)
admin.site.register(Lore)
admin.site.register(Location)



