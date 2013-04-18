from django.db import models

from django.core.cache import cache

from django.contrib.auth.models import User

from django_actionkit.models import CorePage, CoreUser


class CompletedAction(models.Model):
    action = models.IntegerField()
    page = models.IntegerField()
    user = models.IntegerField()
    salesforce_id = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, related_name='createdactionassociations_set')
    last_updated_by = models.ForeignKey(User, related_name='updatedactionassociations_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)
    pushed_to_actionkit = models.BooleanField(default=False)

    def __unicode__(self):
        name = cache.get('cauni-%s' % self.id)
        if name == None:
            page = cache.get('actionpage-%s' % self.page)
            if page == None:
                page = CorePage.objects.only('name').get(pk=self.page)
                cache.set('actionpage-%s' % self.page, page, 86400)
            name = "Action %s on page %s by %s %s" % (self.action, page.name, self.created_by.first_name, self.created_by.last_name)
            cache.set('cauni-%s' % self.id, name, 6000)
        return name


class UserAssociation(models.Model):
    user = models.IntegerField()
    salesforce_id = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, related_name='createduserassociations_set')
    last_updated_by = models.ForeignKey(User, related_name='updateduserassociations_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)
    pushed_to_actionkit = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'UserAssociation'
        verbose_name_plural = 'UserAssociations'

    def __unicode__(self):
        name = cache.get('assocation-%s' % self.user)
        if name == None:
            user = CoreUser.objects.get(pk=self.user)
            name = "%s %s = %s" % (user.first_name, user.last_name, self.salesforce_id)
            cache.set('assocation-%s' % self.user, name, 6000)
        return name
