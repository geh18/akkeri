from app import app, render_template, templated
import models
from sqlalchemy import desc


@app.route('/')
@templated('index.html')
def index():
    posts = models.Post.query.filter_by(
            is_draft=False).order_by(desc('published')).limit(20)
    return dict(posts=posts)
