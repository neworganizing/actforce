from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from actforce.apps.base.forms import SalesforceAccountForm
from actforce.apps.base.models import SalesforceAccount

from django.conf import settings

from salesforce_oauth2 import SalesforceOAuth2

from simple_salesforce import Salesforce


class PreferencesView(TemplateView):
    template_name = "preferences.html"

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)

        try:
            initial_username = SalesforceAccount.objects.get(account=request.user).login
        except SalesforceAccount.DoesNotExist:
            initial_username = request.user.email

        context['form'] = SalesforceAccountForm(initial={'login': initial_username})

        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, **kwargs):
        sfaccount, created = SalesforceAccount.objects.get_or_create(account=request.user)
        form = SalesforceAccountForm(request.POST, instance=sfaccount)

        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Saved Account')
            return redirect("/")
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form

        return self.render_to_response(context)


class SFAuthView(View):

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        if 'code' in request.GET:
            code = request.GET['code']

            print "Got Code %s" % code

            oa = SalesforceOAuth2(settings.SF_OAUTH_CLIENT_ID, settings.SF_OAUTH_CLIENT_SECRET, settings.SF_OAUTH_REDIRECT_URI)

            auth_response = oa.get_token(code)

            print auth_response

            if 'error' in auth_response:
                messages.error(request, 'Error %s: %s' % (auth_response['error'], auth_response['error_description']))

            if 'refresh_token' in auth_response:
                refresh_token = auth_response['refresh_token']
                sfaccount, created = SalesforceAccount.objects.get_or_create(account=request.user, defaults={'token': refresh_token})
                if not created and sfaccount.token != refresh_token:
                    sfaccount.token = refresh_token
                    print "Code Changed to %s" % refresh_token
                    sfaccount.save()
                messages.success(request, "Success!")

            if 'access_token' in auth_response and 'instance_url' in auth_response:
                request.session['sf_instance'] = auth_response['instance_url']
                request.session['sf_session'] = auth_response['access_token']

            return redirect("/")

        else:
            print "No Code!"
            messages.warning(request, 'No Code Found In Salesforce Authentication URL')
            return redirect("/")
