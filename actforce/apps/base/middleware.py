from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

import re

from salesforce_oauth2 import SalesforceOAuth2

from actforce.apps.base.models import SalesforceAccount
from actforce.apps.base.salesforce import refresh_token


class SalesforceMiddleware:
    def process_request(self, request):
        path = request.path

        #if 'sf_session' in request.session:
        #    print "Session Auth: %s " % request.session['sf_session']

        oa = SalesforceOAuth2(settings.SF_OAUTH_CLIENT_ID, settings.SF_OAUTH_CLIENT_SECRET, settings.SF_OAUTH_REDIRECT_URI)

        # User is authenticated but does not have a salesforce session (and isn't in the process of getting one, or in the admin)
        if hasattr(request, 'user') and request.user.is_authenticated() and ('sf_instance' or 'sf_session') not in request.session and '/sfauth/' not in path and '/admin/' not in path:
            print "Trying to Pull"
            # Try to pull the user's refresh token
            try:
                sfinfo = SalesforceAccount.objects.get(account=request.user)
            except SalesforceAccount.DoesNotExist:
                print "No Refresh Token"
                # We don't have any refresh token
                return redirect(oa.authorize_url())

            try:
                refresh_result = oa.refresh_token(sfinfo.token)
                print refresh_result
                if 'access_token' not in refresh_result:
                    print "No Access Token Found"
                else:
                    request.session['sf_instance'] = refresh_result['instance_url']
                    request.session['sf_session'] = refresh_result['access_token']
                    print "Salesforce Session Added! Token: %s" % request.session['sf_session']
            except Exception, e:
                # Not sure what the exception is, but lets try authorizing the person again
                # Can clean this up in the future!
                print "Refresh Error %s" % e
                messages.error(request, 'Account Issue: %s' % e)
                return redirect(oa.authorize_url())


class ForceSSL(object):
    """
    Force all requests to use HTTPS
    Adapted from `django-sslify` and this stack overflow thread
    http://stackoverflow.com/questions/8436666/how-to-make-python-on-heroku-https-only
    """
    def process_request(self, request):
        if not request.META.get('HTTP_X_FORWARDED_PROTO', '') == 'https' and not request.is_secure() and settings.FORCE_SSL == True:
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return redirect(secure_url)
