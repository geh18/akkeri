# encoding=utf-8
from jinja2 import contextfilter
from app import app


@contextfilter
@app.template_filter('getattr')
def call_macro_by_name(context, macro_name, *args, **kwargs):
    return context.vars[macro_name](*args, **kwargs)


@app.template_filter('format_date')
def format_date(date, format='%b, %Y'):
    return date.strftime(format)
