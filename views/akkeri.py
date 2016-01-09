from app import app, render_template
import models


@app.route('/')
def index():
    return render_template('index.html')
