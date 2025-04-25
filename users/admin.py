from django.contrib import admin
from .models import Player, SearchHistory, UserSettings, Notification

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("username","fullname", "email",'masterytitle', "lifelevel", "is_active","last_visit","joined_date", "streak_count", "streak_active")
    
    
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("user","search_query", "search_type", "searched_at")
    
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("player","account_type", "notifications", "appearance")
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient","sender", "created_at")
