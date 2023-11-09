import datetime
import string
import random

import bson

from app import bcrypt
from util import database
from faker import Faker


def generate_random_string(length):
    letters = string.ascii_letters  # This contains both uppercase and lowercase letters
    return ''.join(random.choice(letters) for _ in range(length))


def generate_dummy_users(faker, count, locations):
    """
    Generate dummy users
    :param locations: the locations
    :param faker: faker object
    :param count: number of users to generate
    :return: the users
    """
    # generate a randon 3 character string
    users = []
    for i in range(count):
        user = {
            "username": faker.user_name() + generate_random_string(4),
            "password": bcrypt.generate_password_hash(faker.password()),
            "email": faker.email() + generate_random_string(4),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "address": locations[i],
            "phone_number": faker.phone_number() + generate_random_string(2),
            "events": [],
        }
        users.append(user)
        if i % 2000 == 0:
            print(f"Generated {i} users")
    return users


def generate_dummy_events(faker, db, users):
    """
    Generate 2 dummy events for each user
    :param users: the users
    :param faker: faker object
    :return: the events
    """

    count = len(users) * 2

    events = []
    for i in range(count):
        # print(users[i]["address"])
        lat = users[i // 2]["address"][0]
        lng = users[i // 2]["address"][1]
        event = {
            "name": users[i // 2]["username"] + "'s event " + str(i % 2 + 1),
            "description": faker.text(),
            "organizer": users[i // 2]["username"],
            "date": faker.date_time_this_year(after_now=True, before_now=False),
            "location": {
                "type": "Point",
                "coordinates": [float(lng), float(lat)]
            },
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "phone_number": users[i // 2]["phone_number"],
            "categories": [faker.word() for i in range(3)],
            "image": use_dummy_image(),
            "image_mimetype": "image/jpeg"
        }
        # print(event)
        # Add the event to the list of user's events in the database
        if "events" not in users[i // 2]:
            users[i // 2]["events"] = []
        users[i // 2]["events"].append(event["name"])
        db["Users"].update_one({"username": users[i // 2]["username"]}, {"$set": users[i // 2]})

        events.append(event)
        print(f"Generated {i} events")
    return events


def use_dummy_image():
    with open('images/gs.jpeg', 'rb') as image_file:
        image_data = image_file.read()
    return bson.Binary(image_data)


def main():
    """
    Main function
    :return: None
    """
    mydb = database.connect()
    faker = Faker('en_US')

    locations = []

    # with open('US.txt', 'r') as file:
    #     lines = file.readlines()
    # for line in lines[21269:]:
    #     fields = line.split('\t')
    #
    #     if len(fields) >= 11:
    #         lat = fields[9]
    #         lng = fields[10]
    #
    #         locations.append((lat, lng))
    #
    # users = generate_dummy_users(faker, len(locations), locations)
    # collection = mydb["Users"]
    # collection.delete_many({})
    # collection.insert_many(users)

    # Delete all events from the Events collection
    mydb["Events"].delete_many({})

    # Get all users from the database
    users = list(mydb["Users"].find({}))

    events = generate_dummy_events(faker, mydb, users)

    collection = mydb["Events"]
    # Delete all events from the Events collection
    collection.delete_many({})

    # Insert the events to the database
    collection.insert_many(events)
    # Get all events from the database
    events = list(mydb["Events"].find({}))
    # Print the number of events
    print(len(events))

    # # Add the events to the users
    # for event in events:
    #     organizer = event["organizer"]
    #     for user in users:
    #         if user["username"] == organizer:
    #             if "events" not in user:
    #                 user["events"] = []
    #             user["events"].append(event["name"])
    #             break

    # # Add image_mimetype field to each event
    # for event in events:
    #     event["image_mimetype"] = "image/jpeg"
    #
    # # Update the events in the database
    # collection = mydb["Events"]
    # collection.delete_many({})
    # collection.insert_many(events)


if __name__ == '__main__':
    main()
