from flask import Flask, render_template

import database

app = Flask(__name__, static_url_path='/images', static_folder='images')

mydb = database.connect()


@app.route('/')
def index():
    """
    Render the index page
    :return:
    """
    return render_template('landing.html')


@app.route('/about')
def about():
    """
    Render the about page
    :return:
    """
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
