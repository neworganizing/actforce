from django.db import models
from django.contrib.auth.models import User

from django_fields import fields


class SalesforceAccount(models.Model):
    account = models.OneToOneField(User)
    token = fields.EncryptedCharField(max_length=250, verbose_name=u'Salesforce Refresh Token')

    def __unicode__(self):
        return "{firstname} {lastname} ({username})'s Salesforce Account".format(firstname=self.account.first_name, lastname=self.account.last_name, username=self.account.username)
