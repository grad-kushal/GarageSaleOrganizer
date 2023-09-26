import os

from flask import Flask, render_template, request

from util import database

app = Flask(__name__, static_url_path='/static', static_folder='static')

mydb = database.connect()

maps_api_key = os.environ.get('GOOGLE_API_KEY')

@app.route('/')
def index():
    """
    Render the index page
    :return:
    """
    return render_template('landing.html', maps_api_key=maps_api_key)


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

    # Get the events from the database using geo-spatial queries
    events = database.get_documents_by_location(mydb, "Events", lat, lng, 50000)
    # sales = database.get_documents(mydb, "Events")
    events = list(events)
    print(events)
    number_of_sales = len(events)
    print(number_of_sales)
    return render_template('results.html', sales=events, number_of_sales=number_of_sales)


def get_human_readable_date(date):
    """
    Get the human readable date
    :param date: date string
    :return: the human readable date
    """
    date = date.split("/")
    month = date[0]
    day = date[1]
    year = date[2]
    if month == "01":
        month = "January"
    elif month == "02":
        month = "February"
    elif month == "03":
        month = "March"
    elif month == "04":
        month = "April"
    elif month == "05":
        month = "May"
    elif month == "06":
        month = "June"
    elif month == "07":
        month = "July"
    elif month == "08":
        month = "August"
    elif month == "09":
        month = "September"
    elif month == "10":
        month = "October"
    elif month == "11":
        month = "November"
    elif month == "12":
        month = "December"
    date = month + " " + day + ", " + year
    return date


@app.route('/event/<event_id>')
def event(event_id):
    """
    Render the event page
    :param event_id:
    :return:
    """
    event = database.get_document_by_id(mydb, "Events", event_id)
    print(event)
    # get datetime object and create date and time and day of week
    date = event['date']
    date = date.strftime("%m/%d/%Y")
    # print type(date)
    print(type(date))
    date = get_human_readable_date(date)
    time = event['date']
    time = time.strftime("%I:%M %p")
    day_of_week = event['date']
    day_of_week = day_of_week.strftime("%A")
    print(date, time, day_of_week)

    return render_template('event.html', event=event, date=date, time=time, day_of_week=day_of_week)


@app.route('/create')
def create():
    """
    Render the create page
    :return:
    """
    return render_template('create.html')


@app.errorhandler(404)
def page_not_found(e):
    """
    Render the error page
    :param e:
    :return:
    """
    # print("404", e)
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
