from django.contrib import admin
from .models import Player, SearchHistory, UserSettings

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("username","fullname", "email",'masterytitle', "lifelevel", "is_active")
    
    
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("user","search_query", "search_type", "searched_at")
    
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("player","account_type", "notifications", "appearance")
    
