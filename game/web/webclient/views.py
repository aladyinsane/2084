"""
Game-specific webclient views.
"""

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def mobile(request):
    """
    A lightweight, phone-friendly webclient: same evennia.js protocol layer
    as the desktop client, no GoldenLayout/Bootstrap — one output pane, one
    input bar. Phase 1 of the mobile client plan
    (docs/research/mobile-web-client.md).
    """
    if not settings.WEBCLIENT_ENABLED:
        raise Http404
    pagevars = {"browser_sessid": request.session.session_key}
    return render(request, "mobile.html", pagevars)
