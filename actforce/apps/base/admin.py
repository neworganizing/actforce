from django.contrib import admin
from actforce.apps.base.models import *


class SalesforceAccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(SalesforceAccount, SalesforceAccountAdmin)
