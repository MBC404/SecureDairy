from django.contrib import admin
from .models import Connection, Letter, LetterVersion

admin.site.register(Connection)
admin.site.register(Letter)
admin.site.register(LetterVersion)
