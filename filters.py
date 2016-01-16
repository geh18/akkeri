# encoding=utf-8
from jinja2 import Environment, contextfilter
from app import app


@contextfilter
@app.template_filter('getattr')
def call_macro_by_name(context, macro_name, *args, **kwargs):
    return context.vars[macro_name](*args, **kwargs)


@app.template_filter('article_display')
def article_display(index):
    display = [1, 1, 2, 3, 0, 1, 1, 1, 1, 3]
    
    i = display[index%len(display)]

    displays = {0: 'cover_news', 1: 'article_item_1', 2:
    'article_item_2', 3: 'article_item_3'}
    
    return displays.get(i, 'article_item_2')
