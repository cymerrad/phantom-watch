from django_jinja import library
import jinja2

@library.test(name="one")
def is_one(n):
    """
    Usage: {% if m is one %}Foo{% endif %}
    """
    return n == 1

@library.filter
def mylower(name):
    """
    Usage: {{ 'Hello'|mylower() }}
    """
    return name.lower()

@library.filter
@jinja2.contextfilter
def replace(context, value, x, y):
    """
    Filter with template context. Usage: {{ 'Hello'|replace('H','M') }}
    """
    return value.replace(x, y)


@library.global_function
def myecho(data):
    """
    Usage: {{ myecho('foo') }}
    """
    return data


@library.global_function
@library.render_with("test-render-with.jinja")
def myrenderwith(*args, **kwargs):
    """
    Render result with jinja template. Usage: {{ myrenderwith() }}
    """
    return {"name": "Foo"}