import os
from app import create_app, db
from app.models import User, Role, Follow
from flask_script import Manager, Shell

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
	app.run()
