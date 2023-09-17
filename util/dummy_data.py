import datetime

from util import database
from faker import Faker


def generate_dummy_users(faker, count):
    """
    Generate dummy users
    :param faker: faker object
    :param count: number of users to generate
    :return: the users
    """
    users = []
    for i in range(count):
        user = {
            "username": faker.user_name(),
            "password": faker.password(),
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "address": faker.address(),
            "phone_number": faker.phone_number()
        }
        users.append(user)
    return users


def generate_dummy_events(faker, users, count):
    """
    Generate dummy events
    :param faker: faker object
    :param count: number of events to generate
    :return: the events
    """
    events = []
    for i in range(count):
        event = {
            "name": users[i]["username"] + "'s event",
            "description": faker.text(),
            "organizer": users[i]["username"],
            "date": faker.date_time_this_year(after_now=True, before_now=False),
            "location": {
                "type": "Point",
                "coordinates": [float(faker.longitude()), float(faker.latitude())]
            },
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "phone_number": faker.phone_number(),
            "categories": [faker.word() for i in range(3)]
        }
        print(event)
        events.append(event)
    return events


def main():
    """
    Main function
    :return: None
    """
    mydb = database.connect()
    faker = Faker()

    users = generate_dummy_users(faker, 100)
    collection = mydb["Users"]
    collection.delete_many({})
    collection.insert_many(users)

    events = generate_dummy_events(faker, users, 100)
    collection = mydb["Events"]
    collection.delete_many({})
    collection.insert_many(events)


if __name__ == '__main__':
    main()
