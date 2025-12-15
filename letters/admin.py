from django.contrib import admin
from .models import Connection, Letter, LetterVersion



admin.site.register(Connection)
admin.site.register(Letter)
admin.site.register(LetterVersion)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("requester", "receiver", "accepted", "created_at")
    list_filter = ("accepted",)


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "created_at")


@admin.register(LetterVersion)
class LetterVersionAdmin(admin.ModelAdmin):
    list_display = ("letter", "approved", "created_at")
