# Garage Sale Organizer

Welcome to the Garage Sale Organizer project! This web-based platform is designed to help users discover the best garage sales in their local area. Below, you'll find a detailed explanation of the project and its various endpoints.

## Project Overview

The Garage Sale Organizer project aims to simplify the process of finding and attending garage sales. It provides a user-friendly interface for searching, viewing event details, and interacting with the community of garage sale enthusiasts.

## Webpages and Endpoints

### Landing Page
- URL: `/`
- Description: The landing page provides an introduction to the project and its features. Users can start searching for garage sales by entering their ZIP code or location coordinates.

### About Us Page
- URL: `/about`
- Description: Learn more about the project, its mission, and the team behind it. This page provides insights into the goals and aspirations of the Garage Sale Organizer.

### Search Results Page
- URL: `/search`
- Description: Users can access this page after performing a search for garage sales. It displays a list of all the garage sales found near the user's location, along with relevant details.

### Event Details Page
- URL: `/event/<event_id>`
- Description: Each garage sale event has a dedicated details page. Users can access this page by clicking "View Details" from the search results. It displays a wide event picture, event name, date, location, and event description.

### User Authentication (Upcoming)
- URLs: `/login`, `/register`, `/logout`
- Description: User authentication will be implemented in the next milestone. Users will be able to register, log in, and log out to access advanced features such as marking events as favorites, leaving reviews, and creating their own events.

### User Profile (Upcoming)
- URL: `/profile/<user_id>`
- Description: Users will have individual profiles that display their information, favorite events, and activity within the community.

### Create Event (Upcoming)
- URL: `/create_event`
- Description: In the future, users will be able to create and manage their garage sale events. This page will allow event organizers to provide event details and images.

## Technologies Used

- **Flask**: Used as the web framework for handling routes and rendering templates.
- **MongoDB**: Serves as the database for storing user data, event details, and community interactions.
- **Bootstrap**: Provides the front-end framework for responsive and visually appealing webpages.
- **GeoJSON and Geospatial Indexes**: Enables geospatial queries for finding garage sales near a user's location.

## Installation and Usage

1. Clone the repository: `git clone https://github.com/yourusername/garage-sale-organizer.git`
2. Install required dependencies: `pip install -r requirements.txt`
3. Configure your MongoDB connection in `config.py`.
4. Run the Flask app: `python app.py`
5. Access the app in your browser: `http://localhost:5000`
---

Enjoy discovering and organizing garage sales with the Garage Sale Organizer!
