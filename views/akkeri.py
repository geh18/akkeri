from app import app, templated
from flask import abort, request, jsonify
import models
from manage import db
from sqlalchemy import desc


@app.route('/')
@templated('index.html')
def index():
    featured = {0: 'cover_post', 
                5: 'article_item_2',
                6: 'article_item_3'}

    posts = _get_posts().all()
    
    if len(posts) > 6:
        for key in featured:
            a = _get_by_display(posts, featured[key])
            if a:
                posts = _switch_places(posts, a, key)
    
    return locals()


@app.route('/post/<path:slug>/')
@templated('post.html')
def post(slug):
    post = _get_post(models.Post.POST_TYPE_IDS, slug)
    side_posts = _get_posts().filter(models.Post.id!=post.id)[:8]
    p = models.Post
    pages = p.query.\
                filter_by(is_draft=False).\
                filter(p.post_type_id.in_((p.PAGE_TYPE_ID,)))
    
    return dict(post=post, side_posts=side_posts, pages=pages)


@app.route('/page/<path:slug>/')
@templated('page.html')
def page(slug):
    post = _get_post(models.Post.PAGE_TYPE_ID, slug)
    side_posts = _get_posts().filter(models.Post.id!=post.id)[:6]
    return dict(post=post, side_posts=side_posts)


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


def _get_by_display(posts, post_display):
    index = next((i for i, post in enumerate(posts)
                 if post.post_display and
                 post.post_display.label == post_display), None)

    return index


def _switch_places(ls, a, b):
    # ls = [x0, x1, ..., xi], a,b = [0,...i]
    # ls2 = _switch_places(ls, a, b) 
    # ls2 ls[a] => ls[b] && ls[b] => ls[a]
    ls[b], ls[a] = ls[a], ls[b]
    return ls


def _get_posts():
    p = models.Post
    return p.query.\
        filter_by(is_draft=False).\
        filter(p.post_type_id.in_(p.POST_TYPE_IDS)).\
        order_by(desc(models.Post.published))


@app.route('/modal_upload_image', methods=['GET', 'POST'])
@templated('modal_upload_image.html')
def modal_upload_image():
    from forms import ImageWithPreviewForm
    from flask_admin.helpers import get_form_data
    from models import Image
    from helpers import base64_decode
    from werkzeug.datastructures import FileStorage, ImmutableMultiDict
    import io
    import flask_login
    from models import Post
    from app import thumb

    resp = {}

    decoded_data = base64_decode(request.form.get('image_path'))
    if decoded_data:
        try:
            file_data = io.BytesIO(decoded_data)
            file = FileStorage(file_data, filename='virtual.jpg')
            request.files = ImmutableMultiDict([('image_path', file)])
        except:
            request.files = ImmutableMultiDict([])

    form = ImageWithPreviewForm(get_form_data(), obj=Image)

    if request.method == 'POST' and form.validate():
        postid = request.form.get('postid')
        if postid is None:
            post = Post(author=flask_login.current_user, title='')
            db.session.add(post)
            db.session.commit()
            postid = post.id
            resp['new'] = True
            resp['postid'] = postid

        img = Image(owner=flask_login.current_user, post_id=postid)
        db.session.add(img)
        db.session.commit()
        form.populate_obj(img)
        db.session.commit()
        resp['img_path'] = thumb.thumbnail(img.image_path, '400x', crop=False)
        resp['img_id'] = img.id

        return jsonify(**resp)

    resp['form'] = form

    return resp

