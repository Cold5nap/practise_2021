import flask_admin
import flask_login as login
from flask import url_for, redirect, request, abort
from flask_admin import expose
from flask_admin.contrib import sqla
from flask_login import current_user


class UserModelView(sqla.ModelView):
    column_exclude_list = 'active'

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin')
                )

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


# Переадресация страниц (используется в шаблонах)
class AdminIndexView(flask_admin.AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login_page'))
        return super(AdminIndexView, self).index()

    @expose('login', methods=('GET', 'POST'))
    def login_page(self):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return super(AdminIndexView, self).index()

    @expose('logout')
    def logout_page(self):
        login.logout_user()
        return redirect(url_for('index'))

    @expose('/reset/')
    def reset_page(self):
        return redirect(url_for('index'))
