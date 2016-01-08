from app import app, render_template
import models


@app.route('/')
def frontpage():
    return render_template('hello.html')
