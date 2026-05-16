from django.contrib import admin
from notes import models

# Register your models here.
# admin.site.register(models.Sheet_Music)
admin.site.register(models.Reading_Notes)
admin.site.register(models.Travel_Notes)
admin.site.register(models.Life_Notes)
admin.site.register(models.ReadingNoteLike)
admin.site.register(models.TravelNoteLike)
admin.site.register(models.LifeNoteLike)
admin.site.register(models.ReadingNoteComment)
admin.site.register(models.TravelNoteComment)
admin.site.register(models.LifeNoteComment)