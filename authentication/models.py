from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    __tablename__ = "users"

    userId = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    roles = database.Column(database.String(16), nullable=False)

    def __repr__(self):
        return "{} {} {} {}".format(self.email, self.forename, self.surname, self.roles)