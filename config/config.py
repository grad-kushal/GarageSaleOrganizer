import util.secret_key

DEBUG = True
SECRET_KEY = util.secret_key.generate_secret_key(32)

MONGODB_HOST = 'mongodb://localhost:27017/'
DATABASE_NAME = 'GarageSaleOrganizer'


