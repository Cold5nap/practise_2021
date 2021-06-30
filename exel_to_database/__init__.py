import os

import flask_admin
from flask import url_for, Flask
from flask_admin import helpers
from flask_cors import CORS
from flask_login import LoginManager
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy

from exel_to_database.views import UserModelView, AdminIndexView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DB_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../DBs')
app.config['EXCEL_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ExcelFiles')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECURITY_MSG_LOGIN'] = ('Возможности сайта доступны лишь водшему в учетную запись пользователю.', 'error')

CORS(app)
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

login_manager = LoginManager(app)

from exel_to_database import models, routes
from exel_to_database.models import User, Role, File

# Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
admin = flask_admin.Admin(app, name='Администратор', index_view=AdminIndexView(),
                          base_template='admin/master-extended.html')
admin.add_view(UserModelView(User, db.session, name="Пользователи"))
admin.add_view(UserModelView(File, db.session, name='Файлы Excel'))# , name="ФайлыExcel"
db.create_all()


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=helpers,
        get_url=url_for
    )


# Регистрация путей Blueprint
from exel_to_database.routes import admin_bp

app.register_blueprint(admin_bp, url_prefix="/admin")
