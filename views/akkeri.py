from app import app, templated
from flask import abort
import models


@app.route('/')
@templated('index.html')
def index():
    posts = models.Post.query.filter_by(is_draft=False).all()

    index = next((i for i, post in enumerate(posts)
                 if post.post_display and
                 post.post_display[0].display == u'cover_post'), 0)

    cover_post = posts.pop(index)

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
