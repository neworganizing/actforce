from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from salesforce_oauth2 import SalesforceOAuth2

from simple_salesforce import Salesforce, SalesforceGeneralError

from actforce.apps.base.models import SalesforceAccount


def refresh_token(request):
    print "Refreshing Token!"
    try:
        sfinfo = SalesforceAccount.objects.get(account=request.user)
    except SalesforceAccount.DoesNotExist:
        print "No Refresh Token"
        # We don't have any refresh token
        return redirect(oa.authorize_url())

    oa = SalesforceOAuth2(settings.SF_OAUTH_CLIENT_ID, settings.SF_OAUTH_CLIENT_SECRET, settings.SF_OAUTH_REDIRECT_URI)

    try:
        refresh_result = oa.refresh_token(sfinfo.token)
        print refresh_result
        if 'access_token' not in refresh_result:
            print "No Access Token Found"
        else:
            request.session['sf_instance'] = refresh_result['instance_url']
            request.session['sf_session'] = refresh_result['access_token']
            print "Salesforce Session Added! Token: %s" % request.session['sf_session']
            return Salesforce(instance_url=refresh_result['instance_url'], session_id=request.session['sf_session'])
    except Exception, e:
        # Not sure what the exception is
        print "Refresh Error %s" % e
        messages.error(request, 'Account Issue: %s' % e)
        raise Exception(e)
