from app import app, templated
from flask import abort
import models

def get_by_display(posts, post_display):
    index = next((i for i, post in enumerate(posts)
                 if post.post_display and
                 post.post_display.label == post_display), None)

    return index


def switch_places(ls, a, b):
    # ls = [x0, x1, ..., xi], a,b = [0,...i]
    # ls2 = switch_places(ls, a, b) 
    # ls2 ls[a] => ls[b] && ls[b] => ls[a]
    ls[b], ls[a] = ls[a], ls[b]
    return ls


@app.route('/')
@templated('index.html')
def index():
    featured = {0: 'cover_post', 
                5: 'article_item_2',
                6: 'article_item_3'}

    p = models.Post
    posts = p.query.\
                filter_by(is_draft=False).\
                filter(p.post_type_id.in_(p.POST_TYPE_IDS)).\
                all()

    
    for key in featured:
        a = get_by_display(posts, featured[key])
        if a:
            posts = switch_places(posts, a, key)
    
    return locals()


@app.route('/post/<path:slug>/')
@templated('post.html')
def post(slug):
    post = _get_post(models.Post.POST_TYPE_IDS, slug)
    return dict(post=post)


@app.route('/page/<path:slug>/')
@templated('page.html')
def page(slug):
    post = _get_post(models.Post.PAGE_TYPE_ID, slug)
    return dict(post=post)


@app.route('/profile/<path:slug>/')
@templated('profile.html')
def profile(slug):
    post = _get_post(models.Post.PROFILE_TYPE_ID, slug)
    return dict(post=post)


def _get_post(type_ids, slug):
    if isinstance(type_ids, int):
        type_ids = (type_ids, )
    p = models.Post
    post = p.query.filter_by(
            slug=slug, is_draft=False).filter(
            p.post_type_id.in_(type_ids)).one_or_none()
    if not post:
        abort(404)
    return post
