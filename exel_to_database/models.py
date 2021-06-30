from datetime import datetime
from flask_login import UserMixin
from flask_security import RoleMixin
from exel_to_database import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    path = db.Column(db.String(200), nullable=False, unique=True)

    def __repr__(self):
        return "<File('%s', '%s')>" % (self.name, self.path)


files_users = db.Table(
    'files_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('file_id', db.Integer(), db.ForeignKey('files.id'))
)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Role('%s')>" % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    # Нужен для security!
    active = db.Column(db.Boolean())
    _roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    _files = db.relationship('File', cascade="all,delete", secondary=files_users)#, backref=db.backref('users', lazy='dynamic'))

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, all_roles):
        self._roles = all_roles

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, all_files):
        self._files = all_files

    # Flask - Login
    @property
    def is_admin(self):
        return 'admin' in self._roles

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Flask-Security
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % (self.login, self._roles, self._files)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
