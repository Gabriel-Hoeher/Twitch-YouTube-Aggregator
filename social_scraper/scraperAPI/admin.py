from django.contrib import admin
from .models import Media, CreatorInfo, CreatorLiveStatus

admin.site.register(Media)
admin.site.register(CreatorInfo)
admin.site.register(CreatorLiveStatus)