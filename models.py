class User:
    def __init__(self, username, password, email, first_name, last_name, address, phone_number, events, is_active=True, user_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number
        self.is_active = is_active
        self.events = events
        self._authenticated = False

    def get_id(self):
        return str(self.user_id)

    def is_authenticated(self):
        return self._authenticated

    def set_authenticated(self, value):
        self._authenticated = value


class Event:
    def __init__(self, name, description, datetime, location, organizer, categories, image=None, image_mime_type=None):
        self.name = name
        self.description = description
        self.organizer = organizer.username
        self.phone_number = organizer.phone_number
        self.date = datetime
        self.location = location
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.categories = categories
        self.image = image
        self.image_mimetype = image_mime_type
