class User:
    def __init__(self, username, password, email, first_name, last_name, address, phone_number, is_active=True, user_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number
        self.is_active = is_active
        self._authenticated = False

    def get_id(self):
        return str(self.user_id)

    def is_authenticated(self):
        return self._authenticated

    def set_authenticated(self, value):
        self._authenticated = value
