from django.contrib import admin
from actforce.apps.mover.models import *


class CompletedActionAdmin(admin.ModelAdmin):
    pass


class UserAssociationAdmin(admin.ModelAdmin):
    pass

admin.site.register(CompletedAction, CompletedActionAdmin)
admin.site.register(UserAssociation, UserAssociationAdmin)
