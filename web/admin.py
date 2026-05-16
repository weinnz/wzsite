from django.contrib import admin
from web import models

# Register your models here.
admin.site.register(models.Explorer)
admin.site.register(models.Message)
admin.site.register(models.SiteInfo)
admin.site.register(models.BGImg)