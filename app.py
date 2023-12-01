import base64
import os
from datetime import datetime
from io import BytesIO
from pprint import pprint

import requests
from PIL import Image
from bson import Binary, ObjectId
from flask import Flask, render_template, request, flash, url_for, redirect, jsonify
import flask_login
from flask_bcrypt import Bcrypt

from config import config
from models import User, Event
from util import database, pathplanning

app = Flask(__name__, static_url_path='/images', static_folder='images')

lm = flask_login.LoginManager(app)
lm.init_app(app)

bcrypt = Bcrypt(app)

lm.login_view = 'login'

mydb = database.connect()

maps_api_key = os.environ.get('GOOGLE_API_KEY')

geocoding_base_url = "https://maps.googleapis.com/maps/api/geocode/json?address="

# app.config['SECRET_KEY'] = config.SECRET_KEY

# flask.Config['FLASK_LOGIN_USE_URL_ENCODE'] = False
# flask.Config['FLASK_LOGIN_USE_URL_DECODE'] = False

app.config.from_object(config)


@app.route('/')
@flask_login.login_required
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
@flask_login.login_required
def search():
    """
    Render the search page
    :return:
    """
    location = request.args.get('location')
    print("ZZZ: ", location)
    event_date = request.args.get('date')
    print(event_date)

    if event_date:
        event_date = datetime.strptime(event_date, "%Y-%m-%d")
    if event_date == "":
        # set default date to today
        print("No date")
        event_date = datetime.today().strftime('%Y-%m-%d')
        event_date = datetime.strptime(event_date, "%Y-%m-%d")
    if not event_date:
        # set default date to today
        print("No date")
        event_date = datetime.today().strftime('%Y-%m-%d')
        event_date = datetime.strptime(event_date, "%Y-%m-%d")

    start_of_day = event_date.replace(hour=0, minute=0)
    end_of_day = event_date.replace(hour=23, minute=59)

    # Check if the location is a zip code or a point with lat and lng
    if len(location) == 5 and location.isdigit():
        # Get the coordinates of the zip code
        url = geocoding_base_url + location + "&key=" + maps_api_key
        response = requests.get(url)
        response = response.json()
        print(response)
        if response['status'] == "OK":
            lat = response['results'][0]['geometry']['location']['lat']
            lng = response['results'][0]['geometry']['location']['lng']
            # print(lat, lng)
    else:
        loc = location.replace("(", "").replace(")", "").split(",")
        print(loc)
        lat = float(loc[0].strip())
        lng = float(loc[1].strip())
        # print(lat, lng)

    # Get the events on and after the event date from the database using geospatial queries
    events = database.get_documents_by_location_and_date(mydb, "Events", lng, lat,
                                                         50000, start_of_day, end_of_day)
    # events = database.get_documents_by_location(mydb, "Events", lng, lat, 5000)
    # sales = database.get_documents(mydb, "Events")
    events = list(events)
    # print(events)
    number_of_sales = len(events)
    print(number_of_sales)

    utf8_event_images = []
    # Base64 encode the image data and decode it utf-8 for rendering
    for event in events:
        image_data = event['image']
        image_data = base64.b64encode(image_data).decode('utf-8')
        utf8_event_images.append(image_data)

    combined = zip(events, utf8_event_images)

    return render_template('results.html', number_of_sales=number_of_sales, combined=combined,
                           user_location=(lat, lng))


def get_human_readable_date(date):
    """
    Get the human-readable date
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


@app.route('/itinerary', methods=["POST"])
@flask_login.login_required
def itinerary():
    selected_events = request.form.getlist('selected_events')
    print(selected_events)
    print(type(selected_events))
    user_location = request.form['user_location']
    print("LLLLLL: ", user_location)
    # convert the user location to lat and lng
    loc = (user_location.replace("(", "").replace(")", "").split(","))
    print(loc)
    lat = float(loc[0].strip())
    lng = float(loc[1].strip())
    print("LATLANG: ", lat, lng)
    selected_events = [ObjectId(event_id) for event_id in selected_events]
    # print(selected_events)
    # print(type(selected_events))

    # Get the events from the database
    events = []
    for event_id in selected_events:
        event = database.get_document_by_id(mydb, "Events", event_id)
        events.append(event)

    # Create home event and add it to the events list at the beginning
    home_event = {
        "_id": "Home",
        "name": "Home",
        "description": "Home",
        "location": {
            "type": "Point",
            "coordinates": [lng, lat]
        }
    }
    print(len(events))
    events.insert(0, home_event)
    print(len(events))

    # Create an id to name map for the events
    id_to_name_map = {str(event['_id']): (event['name'], event['location']['coordinates']) for event in events}

    # create a matrix of distances between events
    coordinates_list = [event['location']['coordinates'] for event in events]
    # Add the user location to the coordinates list at the beginning
    # coordinates_list.insert(0, (lng, lat))
    resp = pathplanning.get_distance_matrix(coordinates_list)

    # print(resp)

    distance_matrix = []
    duration_matrix = []

    for row in resp['rows']:
        row_list = [row['elements'][i]['distance']['value'] for i in range(len(row['elements']))]
        distance_matrix.append(row_list)
        row_list = [row['elements'][i]['duration']['value'] for i in range(len(row['elements']))]
        duration_matrix.append(row_list)

    for row in distance_matrix:
        print(row)

    # Create a cost matrix for the events by considering both distance and duration
    # cost_matrix = pathplanning.create_cost_matrix(distance_matrix, duration_matrix, 0.6, 0.4)
    #
    # # print cost matrix
    # for cost in cost_matrix:
    #     print("Cost: ", cost)

    # Solve the TSP using the cost matrix
    dist_preferred_routes = pathplanning.solve_tsp(distance_matrix, "Distance")
    dur_preferred_routes = pathplanning.solve_tsp(duration_matrix, "Duration")

    # print(dist_preferred_routes)
    # print(dur_preferred_routes)

    for event in events:
        print(event['name'])

    # Generate event names and locations for the preferred routes
    # print("Events: ", events)
    for route in dist_preferred_routes:
        print("Route: ", route)
        for event in route:
            print("events[event]['_id']: ", events[event]['_id'])
            print("Event: ", id_to_name_map[str(events[event]['_id'])])
    for route in dur_preferred_routes:
        print("Route: ", route)
        for event in route:
            print("Event: ", id_to_name_map[str(events[event]['_id'])])

    dist_preferred_routes_with_names_and_locations = []
    dur_preferred_routes_with_names_and_locations = []
    for route in dist_preferred_routes:
        route_with_names_and_locations = []
        for event in route:
            route_with_names_and_locations.append(id_to_name_map[str(events[event]['_id'])])
        dist_preferred_routes_with_names_and_locations.append(route_with_names_and_locations)

    for route in dur_preferred_routes:
        route_with_names_and_locations = []
        for event in route:
            route_with_names_and_locations.append(id_to_name_map[str(events[event]['_id'])])
        dur_preferred_routes_with_names_and_locations.append(route_with_names_and_locations)

    print(dist_preferred_routes_with_names_and_locations)
    print(dur_preferred_routes_with_names_and_locations)

    return render_template('itinerary.html', dist_preferred_routes=dist_preferred_routes_with_names_and_locations,
                           dur_preferred_routes=dur_preferred_routes_with_names_and_locations, user_location=(lat, lng))

    # if dist_preferred_routes and dur_preferred_routes:
    #     return render_template('itinerary.html', dist_preferred_routes=dist_preferred_routes,
    #                            dur_preferred_routes=dur_preferred_routes)

    # if dist_preferred_route and dur_preferred_route:
    #     sol_dist = [id_to_name_map[str(events[dist_preferred_route[i]]['_id'])] for i in range(len(dist_preferred_route))]
    #     sol_dur = [id_to_name_map[str(events[dur_preferred_route[i]]['_id'])] for i in range(len(dur_preferred_route))]
    #     return render_template('itinerary.html', sol_dist=sol_dist, sol_dur=sol_dur)
    # elif dist_preferred_route:
    #     sol_dist = [id_to_name_map[str(events[dist_preferred_route[i]]['_id'])] for i in range(len(dist_preferred_route))]
    #     return render_template('itinerary.html', sol_dist=sol_dist)
    # elif dur_preferred_route:
    #     sol_dur = [id_to_name_map[str(events[dur_preferred_route[i]]['_id'])] for i in range(len(dur_preferred_route))]
    #     return render_template('itinerary.html', sol_dur=sol_dur)
    # else:
    return render_template('itinerary.html')


@app.route('/event/<event_id>')
@flask_login.login_required
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

    image_data = event['image']
    image_data = base64.b64encode(image_data).decode('utf-8')
    image_mime_type = event['image_mimetype']

    return render_template('event.html', event=event, date=date, time=time, day_of_week=day_of_week,
                           image_data=image_data, image_mime_type=image_mime_type)


@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
def create():
    """
    Render the create page
    :return:
    """
    if request.method == 'GET':
        # print(maps_api_key)
        return render_template('create.html', maps_api_key=maps_api_key)
    else:
        name = request.form['event_name']
        description = request.form['event_description']
        organizer = flask_login.current_user
        date = request.form['event_date']
        time = request.form['event_time']
        # create mongodb datetime object
        date_time = date + " " + time
        date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        print(date_time)
        # create mongodb point
        location = request.form['event_location']
        loc = location.replace("(", "").replace(")", "").split(",")
        lng = float(loc[0].strip())
        lat = float(loc[1].strip())
        # Round the lat and lng to 6 decimal places
        lati = round(lng, 6)
        lng = round(lat, 6)
        location = {
            "type": "Point",
            "coordinates": [lng, lati]
        }
        categories = request.form['event_categories']
        categories = categories.split(",")
        image_data = None
        image_mime_type = None
        image_file_name = None
        if 'event_image' in request.files:
            image = request.files['event_image']
            if image.filename != '':
                img = Image.open(image)
                img = img.resize((1004, 591))
                img_bytes = BytesIO()
                img.save(img_bytes, format='JPEG')
                image_data = Binary(img_bytes.getvalue())
                image_mime_type = image.mimetype
        my_event = database.get_event_by_name(mydb, name)
        if my_event:
            flash("Event already exists. Use a different name.", "warning")
            return redirect(url_for('create'))
        else:
            new_event = Event(name=name, description=description, organizer=organizer, datetime=date_time,
                              location=location, categories=categories, image=image_data,
                              image_mime_type=image_mime_type)
            res = database.insert_document(mydb, "Events", new_event.__dict__)
            if res and res.acknowledged:
                insert_id = res.inserted_id
                # Add event id and name to user's events list
                database.add_event_to_user(mydb, flask_login.current_user.user_id, insert_id, name)
                flash("Event created successfully.", "success")
                return redirect(url_for('index'))


@lm.user_loader
def load_user(user_id):
    """
    Load the user
    :param user_id: user id
    :return: the user
    """
    user = database.get_document_by_id(mydb, "Users", user_id)
    if user:
        return User(user_id=user['_id'], username=user['username'], password=user['password'], email=user['email'],
                    first_name=user['first_name'], last_name=user['last_name'], address=user['address'],
                    phone_number=user['phone_number'], events=user['events'])
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    r = request
    print("3", request)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("1", username, password)
        next_page = request.form['next']

        user = database.get_user_by_username(mydb, username)

        if user:
            if bcrypt.check_password_hash(user['password'], password):
                user = User(user_id=user['_id'], username=user['username'], password=user['password'],
                            email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                            address=user['address'], phone_number=user['phone_number'], events=user['events'],
                            is_active=True)
                user.set_authenticated(True)
                print(str(user))
                flask_login.login_user(user)
                flash("Logged in successfully.", "success")
                print(next_page)
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))
            else:
                flash("Wrong password.", "danger")
                return redirect(url_for('login'))

        else:
            flash("User does not exist. Create your account!", "warning")
            return redirect(url_for('register'))
    else:
        next_page = request.args.get('next')
        print("next", next_page)
        if next_page:
            return render_template('login.html', error=False, next=next_page)
        else:
            return render_template('login.html', error=False)


@app.route('/profile', methods=['GET'])
@flask_login.login_required
def profile():
    """
    Render the profile page
    :return:
    """
    user = flask_login.current_user
    print(user)
    events = []
    for event in user.events:
        event = database.get_document_by_id(mydb, "Events", event['_id'])
        events.append(event)
    # print(events)
    return render_template('profile.html', user=user, events=events)


@app.route('/logout')
def logout():
    """
    Logout the user
    :return:
    """
    next_page = request.args.get('next')
    flag = flask_login.logout_user()
    print(flag)
    flash("Logged out successfully.", "success")
    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register the user
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        user = database.get_user_by_username(mydb, username)
        events = []
        if user:
            flash("User already exists.Login with your credentials", "warning")
            return redirect(url_for('login'))
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email,
                            first_name=first_name, last_name=last_name, address=address, phone_number=phone_number,
                            events=events)
            database.insert_document(mydb, "Users", new_user.__dict__)
            flash("Registered successfully.", "success")
            return redirect(url_for('login'))
    else:
        return render_template('register.html')


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
