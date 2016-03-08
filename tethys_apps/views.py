"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail

from tethys_apps.app_harvester import SingletonAppHarvester
from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.base.handoff import NEXT_HANDOFF_LIST_KEY, NEXT_HANDOFF_KEY

from tethys_compute.models import TethysJob


@login_required()
def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    harvester = SingletonAppHarvester()

    # Define the context object
    context = {'apps': harvester.apps}

    return render(request, 'tethys_apps/app_library.html', context)

@login_required()
def handoff_capabilities(request, app_name):
    """
    Show handoff capabilities of the app name provided.
    """
    app_name = app_name.replace('-', '_')

    manager = TethysAppBase.get_handoff_manager()
    handlers = manager.get_capabilities(app_name, external_only=True, jsonify=True)

    return HttpResponse(handlers, content_type='application/javascript')


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace('-', '_')

    manager = TethysAppBase.get_handoff_manager()

    # Copy GET QueryDict to make it mutable
    get_parameters = request.GET.copy()

    next_handoff_list = get_parameters.pop(NEXT_HANDOFF_KEY)

    return manager.handoff(request, handler_name, app_name, next_handoff_list, **get_parameters.dict())


@login_required()
def next_handoff(request):
    """
    Handle handoff requests.
    """
    next_handoff_url = request.session[NEXT_HANDOFF_LIST_KEY].pop(0)
    request.session.modified = True
    redirect_url = next_handoff_url

    if ':' in next_handoff_url:
        app_name, handler_name = next_handoff_url.split(':')
        manager = TethysAppBase.get_handoff_manager()
        handler = manager.get_handler(handler_name, app_name)
        if handler:
            redirect_url = reverse(handler(request, **request.GET.dict()))
        else:
            try:
                redirect_url = reverse(next_handoff_url)
            except NoReverseMatch:
                pass

    return redirect('{0}?{1}'.format(redirect_url, request.GET.urlencode()))
    # return redirect(redirect_url)


@login_required()
def send_beta_feedback_email(request):
    """
    Processes and send the beta form data submitted by beta testers
    """
    post = request.POST
    app = None

    # Setup variables
    harvester = SingletonAppHarvester()
    apps_root = 'apps'

    # Get url and parts
    url = post.get('betaFormUrl')
    url_parts = url.split('/')

    # Find the app key
    if apps_root in url_parts:
        # The app root_url is the path item following (+1) the apps_root item
        app_root_url_index = url_parts.index(apps_root) + 1
        app_root_url = url_parts[app_root_url_index]

        # Get list of app dictionaries from the harvester
        apps = harvester.apps

        # If a match can be made, return the app dictionary as part of the context
        for a in apps:
            if a.root_url == app_root_url:
                app = a

    if app is None or not hasattr(app, 'feedback_emails'):
        json = {'success': False,
                'error': 'App not found or feedback_emails not defined in app.py'}
        return JsonResponse(json)

    # Formulate email
    subject = 'User Feedback for {0}'.format(app.name)

    message = 'User: {0}\n'\
              'User Local Time: {1}\n'\
              'UTC Offset in Hours: {2}\n'\
              'App URL: {3}\n'\
              'User Agent: {4}\n'\
              'Vendor: {5}\n'\
              'Comments:\n' \
              '{6}'.\
        format(
            post.get('betaUser'),
            post.get('betaSubmitLocalTime'),
            post.get('betaSubmitUTCOffset'),
            post.get('betaFormUrl'),
            post.get('betaFormUserAgent'),
            post.get('betaFormVendor'),
            post.get('betaUserComments')
        )

    try:
        send_mail(subject, message, from_email=None, recipient_list=app.feedback_emails)
    except Exception as e:
        json = {'success': False,
                'error': 'Failed to send email: ' + e.message}
        return JsonResponse(json)

    json = {'success': True,
            'result': 'Emails sent to specified developers'}
    return JsonResponse(json)


def update_job_status(request, job_id):
    """
    Callback endpoint for jobs to update status.
    """
    try:
        job = TethysJob.objects.filter(id=job_id)[0]
        job.status
        json = {'success': True}
    except Exception, e:
        json = {'success': False}

    return JsonResponse(json)