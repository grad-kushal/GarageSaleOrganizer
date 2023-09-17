from flask import Flask, render_template, request

from util import database

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


@app.route('/search')
def search():
    """
    Render the search page
    :return:
    """
    location = request.args.get('location')
    print(location)
    # Check if the location is a zip code or a point with lat and lng
    if len(location) == 5 and location.isdigit():
        print("Zip code", location)
    else:
        loc = location.replace("(", "").replace(")", "").split(",")
        lat = float(loc[0].strip())
        lng = float(loc[1].strip())
        print(lat, lng)

    # TODO: Get the events from the database using geo-spatial queries
    sales = database.get_documents(mydb, "Events")
    sales = list(sales)
    number_of_sales = len(sales)
    return render_template('results.html', sales=sales, number_of_sales=number_of_sales)


@app.errorhandler(404)
def page_not_found(e):
    """
    Render the error page
    :param e:
    :return:
    """
    print("404", e)
    return render_template('error.html', error=True)


@app.errorhandler(403)
def page_not_found(e):
    """
    Render the error page
    :param e:
    :return:
    """
    print("403", e)
    return render_template('error.html', error=True)


@app.errorhandler(400)
def page_not_found(e):
    """
    Render the error page
    :param e:
    :return:
    """
    print("400", e)
    return render_template('error.html', error=True)


if __name__ == '__main__':
    app.run(debug=True)
