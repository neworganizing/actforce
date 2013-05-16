from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings

from simple_salesforce import Salesforce, SalesforceExpiredSession

from actionkit.models import CoreAction, CorePage, CoreUserfield

from actforce.apps.base.salesforce import refresh_token

from actforce.apps.mover.models import CompletedAction, UserAssociation
from actforce.apps.mover.forms import SalesforceForm
from actforce.apps.mover.salesforce import search_contacts, search_organizations, create_form, associate, processform


class PageListView(TemplateView):
    template_name = "mover/pagelist.html"

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        pages = cache.get('latestpages')
        if not pages:
            pages = CorePage.objects.using('actionkit').all().order_by('-id')[:100]
            cache.set('latestpages', pages, 300)

        context = {
            'pages': pages
        }
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, **kwargs):

        if 'page' in request.POST:
            try:
                page = CorePage.objects.using('actionkit').get(name=request.POST['page'])
                return redirect('/mover/%s/' % page.name)
            except CorePage.DoesNotExist:
                messages.error(request, 'Sorry, Could Not Find Page \'%s\'' % request.POST['page'])
        else:
            messages.error(request, 'Sorry, Could Not Find That Page')

        return redirect('/mover/')


class MoverView(TemplateView):
    template_name = "mover/mover.html"

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        # If this is an 'associate' request (and all the relevant query strings exist) call the 'associate' method
        if ('action' and 'next' and 'akuser' and 'actionid' and 'sfid' and 'akpage' and 'sfakuserid') in request.GET and request.GET['action'] == 'associate':
            return associate(request)

        # If this is an AJAX request and there is an 'orgname' GET request, that means we're searching for organizations.
        if request.is_ajax() and ('orgname') in request.GET:
            return search_organizations(request)

        # Grab the context necessary to display the page during all types of requests
        context = self.get_context_data(**kwargs)
        if type(context) != dict:
            return context

        # Grab the data necessary to prefill the form during GET requests.
        form_initial = context['form_initial']

        context['form'] = SalesforceForm(initial=form_initial)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(MoverView, self).get_context_data(**kwargs)

        # Set request as a local variable (as a shortcut)
        request = self.request

        # Initialize Our Salesforce Session
        sf = Salesforce(instance_url=request.session['sf_instance'], session_id=request.session['sf_session'])

        # Get all the actions for the page, try the cache first
        actions = cache.get('actions-%s' % kwargs['pagename'])
        if not actions:
            actions = CoreAction.objects.using('actionkit').filter(page__name=kwargs['pagename']).select_related('page','user').extra(select=
                {'organization': 'SELECT `core_userfield`.`value` FROM `core_userfield` WHERE (`core_userfield`.`parent_id` = `core_user`.`id` AND `core_userfield`.`name` = \'organization\')',
                'phone': 'SELECT `core_phone`.`normalized_phone` FROM `core_phone` WHERE `core_phone`.`user_id` = `core_user`.`id` ORDER BY case `core_phone`.`type` when \'home\' then 1 when \'mobile\' then 2 when \'work\' then 3 end LIMIT 1'})
            cache.set('actions-%s' % kwargs['pagename'],actions,300)

        # If there are no actions associated with that page, throw an error message and go back to the page list
        if len(actions) == 0:
            messages.info(request, 'Sorry, No Actions Associated With Page \'%s\'' % kwargs['pagename'])
            return redirect('/mover/')

        # If there is an Action ID in the url (aka /page/actionid), extract that action from the full action list
        if 'actionid' in kwargs:
            for x in actions:
                if x.pk == int(kwargs['actionid']):
                    currentaction = x
            if 'currentaction' not in locals():
                messages.info(request, 'Sorry, No Action %s Associated With Page \'%s\'' % (kwargs['actionid'], kwargs['pagename']))
                return redirect('/mover/')
        else:
            # If no action is passed (aka it's just /page/) return the first action
            currentaction = actions[0]

        # Flesh out various aspects of the action. This is mostly for readability
        page = currentaction.page
        user = currentaction.user
        org = currentaction.organization
        phone = currentaction.phone

        # Call the search_contacts method in salesforce.py, which will find us contacts that match our ActionKit user
        sf, sfcontacts, perfectmatch = search_contacts(request, sf, currentaction)

        try:
            uassociation = UserAssociation.objects.get(user=user.pk)
        except UserAssociation.DoesNotExist:
            uassociation = None

        # This part fills up the form. If the URL has action=edit and a Salesforce ID in the querystring, pull fill the form with that data
        if ('action' and 'sfid') in request.GET and request.GET['action'] == 'edit' and request.GET['sfid'] in sfcontacts:
            form_initial = sfcontacts[request.GET['sfid']]
            form_initial.update({'action': 'edit'})
            del sfcontacts[request.GET['sfid']]
        elif uassociation and uassociation.salesforce_id in sfcontacts:
            form_initial = sfcontacts[uassociation.salesforce_id]
            form_initial.update({'action': 'confirm'})
            del sfcontacts[uassociation.salesforce_id]
        elif perfectmatch:
            form_initial = sfcontacts[perfectmatch]
            form_initial.update({'action': 'confirm'})
            del sfcontacts[perfectmatch]
        else:
            # If the page isn't set to 'edit' mode, this will take ActionKit data and prefill the form
            address = user.address1 + "\n" + user.address2 if user.address2 else user.address1
            form_initial = {
                'firstname': user.first_name.title(),
                'lastname': user.last_name.title(),
                'email': user.email,
                'phone': phone,
                'address': address,
                'city': user.city.title(),
                'state': user.state,
                'zip': user.zip,
                # Use the 'Individual' Org ID
                'orgid': settings.DEFAULT_ORG_ID,
                'orgname': 'Individual',
                'action': 'create'
            }

        form_initial['akuserid'] = user.pk
        form_initial.update({
            'akuserid': user.pk,
            'akactionid': currentaction.pk,
            'akpageid': page.pk
        })

        # Since we want to display contacts in some sort of logical order, this will take the dictionary returned and sort it by our weighting
        contacts = []
        for k, v in sfcontacts.iteritems():
            contacts += [(v['weight'], v)]

        sorted_contacts = sorted(contacts, key=lambda contact: contact[0], reverse=True)

        final_contacts = []
        for x, y in sorted_contacts:
            final_contacts += [y]

        # This part iterates over the actions list until it finds the action we're currently on
        # We then use that below to find the 'next' action to send users to. We want to either forward
        # users to the next action in the list or, if we're at the last action, to the first action in the list
        for index, x in enumerate(actions):
            if x.pk == currentaction.pk:
                break

        nextaction = actions[(index + 1) % len(actions)]

        # Here is where we get a list of all the completed actions, we'll match against this in the template
        completions = CompletedAction.objects.filter(page=page.id).values_list('action', flat=True)
        print completions

        context.update({
            'akaction': currentaction,
            'akuser': user,
            'akuserorg': org,
            'akuserphone': phone,
            'akpage': page,
            'akactions': actions,
            'aknextaction': nextaction,
            'sfcontacts': final_contacts,
            'completions': completions,
            'form_initial': form_initial,
            'sfinstance': 'https://{instance}/'.format(instance=sf.sf_instance)
        })

        return context

    @method_decorator(login_required)
    def post(self, request, **kwargs):

        form = SalesforceForm(request.POST)

        # Check to see if the form is valid or not and if we have a page to go to afterwards.
        if form.is_valid() and 'next' in request.POST:
            processform(form, request)
            return redirect(request.POST['next'])
        else:
            # Grab the necessary context to grab the form
            context = self.get_context_data(**kwargs)
            if type(context) != dict:
                return context
            context['displayform'] = True
            context['form'] = SalesforceForm(request.POST)

        return self.render_to_response(context)
