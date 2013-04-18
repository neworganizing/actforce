from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.cache import cache
from django.conf import settings

from simple_salesforce import Salesforce, SalesforceExpiredSession

from actforce.apps.mover.models import CompletedAction, UserAssociation
from actforce.apps.mover.forms import SalesforceForm
from actforce.apps.base.salesforce import refresh_token

from urllib2 import quote, unquote

import json
import base64


def clean(ustring):
    return ustring.replace("'", "%27")


def weight_contact(contact, currentaction):
    weight = 0
    if currentaction.user.id == contact['ActionKit_USER_ID__c']:
        weight += 3.5
    if currentaction.user.email == contact['Email']:
        weight += 3.2
    if currentaction.user.email != contact['Email'] and currentaction.user.email == contact['Alt_Email__c']:
        weight += 3.1
    if contact['Phone'] and currentaction.phone == contact['Phone']:
        weight += 2
    if currentaction.user.first_name == contact['FirstName']:
        weight += 1
    if currentaction.user.last_name == contact['LastName']:
        weight += 0.75
    return weight


def search_contacts(request, sf, currentaction):

    sfcontact_query = u"""SELECT Id, Name, FirstName, LastName, Account.Name, Account.Id, Title, Email,
    Alt_Email__c, Phone, MobilePhone, HomePhone, OtherPhone,
    MailingStreet, MailingCity, MailingState, MailingPostalCode, ActionKit_USER_ID__c
    FROM Contact WHERE
    Email = '{email}'
    OR Alt_Email__c = '{email}'
    OR ActionKit_USER_ID__c = '{actionkitid}'
    """.format(lastname=clean(currentaction.user.last_name), email=currentaction.user.email, actionkitid=currentaction.user.id)

    if currentaction.user.last_name:
        sfcontact_query = sfcontact_query + u"""OR LastName LIKE '%{lastname}%' """.format(lastname=clean(currentaction.user.last_name))

    if currentaction.phone:
        sfcontact_query = sfcontact_query + u"""OR Phone = '{phone}'
        OR MobilePhone = '{phone}'
        OR HomePhone = '{phone}'
        OR OtherPhone = '{phone}'""".format(phone=currentaction.phone)

    sfcontact_query = sfcontact_query + u" ORDER BY LastName, FirstName LIMIT 100"

    try:
        sfresults = sf.query(sfcontact_query)
    except SalesforceExpiredSession:
        sf = refresh_token(request)
        sfresults = sf.query(sfcontact_query)
    sfcontacts = sfresults.get('records', None)

    perfectmatch = None
    results = {}
    for contact in sfcontacts:
        if contact['ActionKit_USER_ID__c'] == str(currentaction.user.id):
            perfectmatch = contact['Id']
        record = {
            'name': contact['Name'],
            'firstname': contact['FirstName'],
            'lastname': contact['LastName'],
            'email': contact['Email'],
            'alt_email': contact['Alt_Email__c'],
            'phone': contact['Phone'],
            'address': contact['MailingStreet'],
            'city': contact['MailingCity'],
            'state': contact['MailingState'],
            'zip': contact['MailingPostalCode'],
            'orgid': contact['Account']['Id'],
            'orgname': contact['Account']['Name'],
            'salesforceid': contact['Id'],
            'weight': weight_contact(contact, currentaction),
            'id': contact['Id'],
            'sfakid': contact['ActionKit_USER_ID__c'],
            'url': "https://{instance}/{id}".format(instance=sf.sf_instance, id=contact['Id'])
        }
        results.update({str(contact['Id']): record})

    return sf, results, perfectmatch


def search_organizations(request):

    sf = Salesforce(instance_url=request.session['sf_instance'], session_id=request.session['sf_session'])

    orgname = u"%{orgname}%".format(orgname=clean(request.GET['orgname'])) if request.GET['orgname'] else settings.DEFAULT_ORG_NAME

    sforg_query = u"SELECT Id, Name FROM Account WHERE Name LIKE '{orgname}'".format(orgname=orgname)

    if 'orgid' in request.GET and request.GET['orgid'] != u'' and request.GET['orgid'] != settings.DEFAULT_ORG_ID:
        print type(request.GET['orgid'])
        sforg_query = sforg_query + u" OR Id = '{orgid}'".format(orgid=clean(request.GET['orgid']))

    sforg_query = sforg_query + u" LIMIT 7"

    hashkey = base64.b64encode(str(sforg_query.__hash__()))

    sfresults = cache.get('orgsearch-%s' % hashkey)
    if sfresults == None:
        try:
            sfresults = sf.query(sforg_query)
        except SalesforceExpiredSession:
            sf = refresh_token(request)
            sfresults = sf.query(sforg_query)
        cache.set('orgsearch-%s' % hashkey, sfresults, 30)

    records = sfresults['records']

    result = {}
    for x in records:
        result.update({x['Id']: x['Name']})

    return HttpResponse(json.dumps(result), content_type="application/json")


def create_form(currentaction):
    # Helper to pull current user
    user = currentaction.user
    phone = currentaction.phone
    organization = currentaction.organization


def associate(request):
    actionid = request.GET['actionid']
    pageid = request.GET['akpage']
    akuser = request.GET['akuser']
    sfid = request.GET['sfid']
    sfakuserid = request.GET['sfakuserid']

    sf = Salesforce(instance_url=request.session['sf_instance'], session_id=request.session['sf_session'])

    try:
        sfresults = sf.Contact.update(sfid, {'ActionKit_USER_ID__c': akuser})
    except SalesforceExpiredSession:
        sf = refresh_token(request)
        sfresults = sf.Contact.update(sfid, {'ActionKit_USER_ID__c': akuser})

    # Create & Verify Action Association
    act_defaults = {
        'page': pageid,
        'user': akuser,
        'created_by': request.user,
        'salesforce_id': sfid,
        'last_updated_by': request.user
    }
    action_association, created = CompletedAction.objects.get_or_create(action=actionid, defaults=act_defaults)
    if created == False and action_association.salesforce_id != sfid:
        action_association.salesforce_id = sfid
        action_association.last_updated_by = request.user
        action_association.save()

    user_defaults = {
        'salesforce_id': sfid,
        'created_by': request.user,
        'last_updated_by': request.user,
    }
    user_association, created = UserAssociation.objects.get_or_create(user=akuser, defaults=user_defaults)
    if created == False and user_association.salesforce_id != sfid:
        user_association.salesforce_id = sfid
        user_association.last_updated_by = request.user
        user_association.save()

    return redirect(request.GET['next'])


def processform(form, request):

    sf = Salesforce(instance_url=request.session['sf_instance'], session_id=request.session['sf_session'])

    data = form.cleaned_data

    print request.POST['submit']

    if 'submit' in request.POST and request.POST['submit'] != 'edit':
        akid = request.POST['akuserid']
    else:
        akid = ''

    if data['orgid'] == 'neworg':
        if len(data['orgname']) > 2:
            try:
                orgresult = sf.Account.create({'Name': data['orgname']})
            except SalesforceExpiredSession:
                sf = refresh_token(request)
                orgresult = sf.Account.create({'Name': data['orgname']})
            print orgresult
            orgid = orgresult['id']
    else:
        orgid = data['orgid']

    datamap = {
        'FirstName': data['firstname'],
        'LastName': data['lastname'],
        'AccountId': orgid,
        'Title': data['title'],
        'Email': data['email'],
        'Alt_Email__c': data['alt_email'],
        'Phone': data['phone'],
        'MailingStreet': data['address'],
        'MailingCity': data['city'],
        'MailingState': data['state'],
        'MailingPostalCode': data['zip'],
        'ActionKit_USER_ID__c': akid
    }

    # Remove All Empty Fields
    datamap = dict([(k, v) for k, v in datamap.items() if len(v) > 0])

    if data['salesforceid']:
        try:
            sfresult = sf.Contact.update(data['salesforceid'], datamap)
        except SalesforceExpiredSession:
            sf = refresh_token(request)
            sfresult = sf.Contact.update(data['salesforceid'], datamap)
        sfid = data['salesforceid']
    else:
        try:
            sfresult = sf.Contact.create(datamap)
        except SalesforceExpiredSession:
            sf = refresh_token(request)
            sfresult = sf.Contact.create(datamap)
        sfid = sfresult['id']

    if akid:
        # Create & Verify Action Association
        act_defaults = {
            'page': data['akpageid'],
            'user': data['akuserid'],
            'created_by': request.user,
            'salesforce_id': sfid,
            'last_updated_by': request.user
        }
        action_association, created = CompletedAction.objects.get_or_create(action=data['akactionid'], defaults=act_defaults)
        if created == False and action_association.salesforce_id != sfid:
            action_association.salesforce_id = sfid
            action_association.last_updated_by = request.user
            action_association.save()

        user_defaults = {
            'salesforce_id': sfid,
            'created_by': request.user,
            'last_updated_by': request.user,
        }
        user_association, created = UserAssociation.objects.get_or_create(user=data['akuserid'], defaults=user_defaults)
        if created == False and user_association.salesforce_id != sfid:
            user_association.salesforce_id = sfid
            user_association.last_updated_by = request.user
            user_association.save()