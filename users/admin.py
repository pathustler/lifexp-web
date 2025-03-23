from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("username","fullname", "email",'masterytitle', "lifelevel", "is_active")
    
    
    
    
