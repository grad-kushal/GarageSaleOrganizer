import re

import pymongo
from bson import ObjectId


def delete_collection(db, collection):
    """
    Delete the specified collection from the database
    :param db: database name
    :param collection: collection name
    :return: the result of the delete operation
    """
    return db[collection].drop()


def connect(connection_string="mongodb://localhost:27017/", database="GarageSaleOrganizer"):
    """
    Connect to the MongoDB server and return a reference to the database.
    :return: a reference to the database
    """
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient(connection_string)
    return client[database]


def insert_document(db, collection, data):
    """
    Insert a document into the specified collection in the database
    :param db: database name
    :param collection: collection name
    :param data: data to insert
    :return: the result of the insert operation
    """
    return db[collection].insert_one(data)


def insert_documents(db, collection, data):
    """
    Insert multiple documents into the specified collection in the database
    :param db: database name
    :param collection: collection name
    :param data: data to insert
    :return: the result of the insert operation
    """
    print("Inserting documents into collection: ", collection)
    return db[collection].insert_many(data)


def main():
    pass


if __name__ == '__main__':
    main()


def get_document_by_id(mydb, collection_name, document_id):
    """
    Get the document by id
    :param mydb: database object
    :param collection_name: collection name
    :param document_id: document id
    :return: the document
    """
    collection = mydb[collection_name]
    document = collection.find_one({'_id': ObjectId(document_id)})
    # print("Document: ", document)
    return document


def get_documents(mydb, collection_name=None, updated_year=None, category=None, rating=None, rating_comparison=None,
                  tags=None, protocols=None, apis=None):
    """
    Get the documents from the database
    :param apis: apis
    :param rating_comparison: rating comparison operator
    :param mydb: database object
    :param collection_name: collection name
    :param updated_year: updated year
    :param category: category
    :param rating: rating
    :param tags: tags
    :param protocols: protocols
    :return: the documents
    """
    # print("Query parameters: ", collection_name, updated_year, category, rating, tags, protocols)
    # Get the collection
    collection = mydb[collection_name]
    # Create the query
    query = {}
    if updated_year and updated_year != 'all':
        pattern = '^' + str(updated_year) + '-.*'
        sub_query = {'$regex': pattern}
        query['updated'] = sub_query
    if category and category != 'all' and collection_name == 'apis':
        query['category'] = category
    if rating_comparison and rating:
        if rating_comparison == 'gt':
            query['rating'] = {'$gt': rating}
        elif rating_comparison == 'lt':
            query['rating'] = {'$lt': rating}
        elif rating_comparison == 'eq':
            query['rating'] = {'$eq': rating}
    if tags and tags != 'all':
        tags = [tag.strip() for tag in tags]
        sub_query = {'$in': tags}  # $in is used to match any of the tag values in the array
        query['tags'] = sub_query
    if apis and apis != 'all' and collection_name == 'mashups':
        sub_query = {'$all': apis}  # $all is used to match all the api values in the array
        query['apis.name'] = sub_query
    if apis and apis != 'all' and collection_name == 'apis':
        sub_query = {'$in': apis}
        query['_id'] = sub_query
    if protocols and protocols != 'all' and collection_name == 'apis':
        protocols = protocols.split(' ')
        sub_query = {'$in': protocols}
        query['protocols'] = sub_query
    # print("Query: ", query)
    # Get the documents
    documents = collection.find(query)
    # Return the documents
    return documents


def get_documents_by_keywords(mydb, collection_name, keywords):
    """
    Get the documents from the database by keywords
    :param mydb: database object
    :param collection_name: collection name
    :param keywords: keywords list
    :return: the documents matching the keywords
    """
    # print("Query parameters: ", collection_name, keywords)
    # Get the collection
    collection = mydb[collection_name]
    # Create the aggregation pipeline
    pipeline = []
    if keywords:
        for keyword in keywords:
            # Create the match stage
            match_stage = {}
            keyword = keyword.strip()
            keyword = re.escape(keyword)
            keyword = keyword.replace('\ ', '.*')
            keyword = '.*' + keyword + '.*'
            sub_query = {'$regex': keyword, '$options': 'i'}
            match_stage['$or'] = [{'title': sub_query}, {'description': sub_query}, {'summary': sub_query}]
            pipeline.append({'$match': match_stage})
    print("Pipeline: ", pipeline)
    # Get the documents
    documents = collection.aggregate(pipeline)
    # Return the documents
    return documents


def execute_aggregation(mydb, collection_name, pipeline):
    """
    Execute the aggregation pipeline
    :param mydb: database object
    :param collection_name: collection name
    :param pipeline: aggregation pipeline
    :return: the documents
    """
    # print("Query parameters: ", collection_name, pipeline)
    # Get the collection
    collection = mydb[collection_name]
    # Get the documents
    documents = collection.aggregate(pipeline)
    # Return the documents
    return documents


def close_database(mydb):
    """
    Close the connection to the database
    :param mydb: database object
    :return: None
    """
    mydb.client.close()


def get_documents_by_location(mydb, collection_name, lat, lng, radius):
    """
    Get the documents from the database by location
    :param mydb: database object
    :param collection_name: collection name
    :param lat: latitude
    :param lng: longitude
    :param radius: radius in meters
    :return: the documents near the location
    """
    print("Query parameters: ", collection_name, lat, lng, radius)
    pipeline = [
        {
            '$geoNear': {
                'near': {
                    'type': 'Point',
                    'coordinates': [lat, lng]
                },
                'distanceField': 'distance',
                'maxDistance': radius,
                'spherical': True
            }
        }
    ]
    # Get the documents
    documents = execute_aggregation(mydb, collection_name, pipeline)
    # Return the documents
    return documents


def get_user_by_username(mydb, username):
    """
    Get the user by username
    :param mydb: database object
    :param username: username
    :return: the user
    """
    collection = mydb['Users']
    query = {'username': username}
    user = collection.find_one(query)
    return user


def get_event_by_name(mydb, name):
    """
    Get the event by name
    :param mydb: database object
    :param name: name
    :return: the event
    """
    collection = mydb['Events']
    query = {'name': name}
    event = collection.find_one(query)
    return event


def add_event_to_user(mydb, user_id, insert_id, event_name):
    """
    Add the event to the user's events list
    :param event_name:
    :param mydb: database object
    :param user_id: user id
    :param insert_id: event id
    :return: the result of the update operation
    """
    collection = mydb['Users']
    query = {'_id': ObjectId(user_id)}
    # Create an event object to insert in the user's events list
    event = {'_id': insert_id, 'name': event_name}
    # Create the update query
    update = {'$push': {'events': event}}
    result = collection.update_one(query, update)
    return result


def get_documents_by_location_and_date(mydb, collection_name, lng, lat, radius, start_of_day, end_of_day):
    """
    Get the documents from the database by location and date
    :param end_of_day:
    :param start_of_day:
    :param mydb: database object
    :param collection_name: collection name
    :param lng: longitude
    :param lat: latitude
    :param radius: radius in meters
    :return: the documents near the location and date
    """
    print("Query parameters: ", collection_name, lng, lat, radius, start_of_day, end_of_day)
    pipeline = [
        {
            '$geoNear': {
                'near': {
                    'type': 'Point',
                    'coordinates': [lng, lat]
                },
                'distanceField': 'distance',
                'maxDistance': radius,
                'spherical': True
            }
        },
        {
            '$match': {
                '$and': [
                    {'date': {'$gte': start_of_day}},
                    {'date': {'$lte': end_of_day}}
                ]
            }
        }
    ]
    # Get the documents
    documents = execute_aggregation(mydb, collection_name, pipeline)
    # Return the documents
    return documents
