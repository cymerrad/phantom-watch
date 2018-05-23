from django_jinja import library
from django import template
from django.template import loader
from django.utils.safestring import SafeData, mark_safe
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape, format_html

# @library.global_function
# def rev(tag):
#     try:
#         return mark_safe(reverse(tag))
#     except NoReverseMatch:
#         return ''

@library.global_function
def myecho(data):
    """
    Usage: {{ myecho('foo') }}
    """
    return data

@library.global_function
def optional_login(request):
    """
    Include a login snippet if REST framework's login view is in the URLconf.
    """
    try:
        login_url = reverse('rest_framework:login')
    except NoReverseMatch:
        return ''

    snippet = "<li><a href='{href}?next={next}'>Log in</a></li>"
    snippet = format_html(snippet, href=login_url, next=escape(request.path))

    return mark_safe(snippet)

@library.global_function
def optional_logout(request, user):
    """
    Include a logout snippet if REST framework's logout view is in the URLconf.
    """
    try:
        logout_url = reverse('rest_framework:logout')
    except NoReverseMatch:
        snippet = format_html('<li class="navbar-text">{user}</li>', user=escape(user))
        return mark_safe(snippet)

    snippet = """<li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
            {user}
            <b class="caret"></b>
        </a>
        <ul class="dropdown-menu">
            <li><a href='{href}?next={next}'>Log out</a></li>
        </ul>
    </li>"""
    snippet = format_html(snippet, user=escape(user), href=logout_url, next=escape(request.path))

    return mark_safe(snippet)