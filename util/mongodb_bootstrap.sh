#!/bin/bash

MONGO_HOST="localhost"
MONGO_PORT="27017"
DATABASE_NAME="GarageSaleOrganizer"

MONGO_COMMANDS=("db.createCollection('Users')"
"db.createCollection('Events')"
"db.createCollection('UserFavorites')"
"db.createCollection('EventImages')"
"db.createCollection('Reviews')"
"db.createCollection('Comments')"
"db.Users.createIndex({ 'username': 1 }, { unique: true })"
"db.Users.createIndex({ 'email': 1 }, { unique: true })"
"db.Events.createIndex({ 'location.coordinates': '2dsphere' })"
"db.Events.createIndex({ 'date': 1, 'event_categories': 1 })"
"db.UserFavorites.createIndex({ 'user_id': 1, 'event_id': 1 })"
"db.Reviews.createIndex({ 'event_id': 1, 'user_id': 1 })"
"db.Comments.createIndex({ 'event_id': 1, 'user_id': 1 })"
)

for cmd in "${MONGO_COMMANDS[@]}"; do
  mongosh "mongodb://${MONGO_HOST}:${MONGO_PORT}/${DATABASE_NAME}" --eval "${cmd}"
done

echo "MongoDB collections and indexes created successfully!"
