from werkzeug.security import check_password_hash

class User():

    def __init__(self, id, email, password, fullname='') -> None:
        self.id = id
        self.email = email
        self.password = password
        self.fullname = fullname

    @classmethod
    def checkPassword(self, hashedPassword, password):
        return check_password_hash(hashedPassword, password)
