import os
from app import create_app, db
from app.models import User, Role, Follow
from flask_script import Manager, Shell
#from flask_migrate import Migrate, MigrateCommend

app = create_app()
manager = Manager(app)
#migrate = Migrate(app, db)

if __name__ == '__main__':
	manager.run()
