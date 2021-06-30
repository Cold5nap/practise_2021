import os
import shutil

from flask import render_template, request, redirect, flash, url_for, Blueprint, session, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from exel_to_database import app, db
from exel_to_database.db_creator import DBCreator
from exel_to_database.models import User, Role, File
from exel_to_database.sql_enums import TypeEnum as TE, ConstraintEnum as CE
from exel_to_database.sql_mapping import MySQLMapClass, SQLiteMapClass

admin_bp = Blueprint('admin_blueprint', __name__)
EXCEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../ExcelFiles')
DB_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../DBs')
CREATORS = {}


@app.route('/', methods=['GET', 'POST'])
@app.route('/practice.html', methods=['GET', 'POST'])
@login_required
def index():
    files = current_user.files

    # приставка к пути файлов обеспечивает уникальность файлов в базе данных
    session['file_prefix'] = '_' + current_user.login + '_'

    # загрузка файла exel
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if filename[-4:] == 'xlsx':
                path = EXCEL_FOLDER + '/' + session['file_prefix'] + filename
                file.save(path)
                session['file_name'] = filename
                session['file_path'] = path

                return redirect(url_for('set_db'))
    return render_template('index.html', files=files)


@app.route('/about/')
def about():
    return render_template('about.html')


# переход для редактирования загруженного файла Exel
@app.route('/edit_file/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_file(id):
    session['file_path'] = File.query.get(id).path
    session['file_name'] = File.query.get(id).name
    return redirect(url_for('set_db'))


@app.route('/delete_file/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_file_by_id(id):
    file_path = File.query.filter_by(id=id).one().path
    if os.path.exists(file_path):
        os.remove(file_path)

    File.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_tmp_file/<string:name>', methods=['GET', 'POST'])
@login_required
def delete_tmp_file_by_name(name):
    origin = ''
    if name[-4:] == 'xlsx':
        origin = EXCEL_FOLDER
    elif name[-2:] == 'db' or name[-3:] == 'txt':
        origin = DB_FOLDER
    path = origin + '/' + name
    if File.query.filter_by(path=path).count() == 0 and os.path.exists(path):
        os.remove(path)

    return redirect(url_for('set_db'))


@app.route('/save_excel/', methods=['GET', 'POST'])
@login_required
def save_excel():
    new_file_name = request.form['file_name']
    new_path = EXCEL_FOLDER + '/' + session['file_prefix'] + new_file_name
    old_path = session['file_path']

    for f in current_user.files:
        if f.name == new_file_name:
            flash('Файл с таким названием уже есть. Используйте другое название для его сохранения.')
            return 'Файл с таким названием уже есть.'
    if not os.path.exists(new_path):
        shutil.copy(old_path, new_path)
        if File.query.filter_by(path=old_path).count() == 0:
            os.remove(old_path)

    current_user.files.append(File(name=new_file_name, path=new_path))
    db.session.commit()
    return 'Успешно'


@app.route('/set_db/', methods=['GET', 'POST'])
@login_required
def set_db():
    creator = DBCreator(session['file_path'])
    CREATORS[session['file_name']] = creator
    return render_template('TablesSettings.html', filename=session['file_name'], tables=creator.tables)


@app.route('/show_table/', methods=['GET', 'POST'])
@login_required
def show_table():
    if request.method == 'POST':
        table_index = request.form.get('index')
        if table_index == 'None':
            return 'Таблицы нет'
        else:
            table_index = int(table_index)
        session['table_index'] = table_index
    else:
        table_index = session['table_index']

    attributes = CREATORS[session['file_name']].tables[table_index].attributes
    all_types_list = TE.all_types_list()
    all_constraints_list = CE.all_constraints_list()
    table_dict = CREATORS[session['file_name']].tables
    return render_template('Table.html', attributes=attributes, all_types_list=all_types_list,
                           all_constraints_list=all_constraints_list, CE=CE, table_dict=table_dict)


@app.route('/create_SQLite/', methods=['GET', 'POST'])
@login_required
def create_SQLite():
    file_name = request.form['file_name'] + '.db'
    if os.path.exists(os.path.join(DB_FOLDER, file_name)):  # удаляем, если такая имеется
        os.remove(os.path.join(DB_FOLDER, file_name))

    errors = CREATORS[session['file_name']].create_SQLite_db(DB_FOLDER, file_name)
    if not len(errors) == 0:
        res = 'Errors: <br>'
        for error in errors:
            res += '%s<br>' % error
        flash(res)

    return file_name


@app.route('/create_MySQL_TXT/', methods=['GET', 'POST'])
@app.route('/create_SQLite_TXT/', methods=['GET', 'POST'])
@login_required
def create_sql_txt():
    file_name = request.form['file_name'] + '.txt'
    if os.path.exists(os.path.join(DB_FOLDER, file_name)):  # удаляем, если такая имеется
        os.remove(os.path.join(DB_FOLDER, file_name))

    if 'create_SQLite_TXT' in request.url:
        CREATORS[session['file_name']].create_sql_txt(DB_FOLDER, file_name, SQLiteMapClass)
    elif 'create_MySQL_TXT' in request.url:
        CREATORS[session['file_name']].create_sql_txt(DB_FOLDER, file_name, MySQLMapClass)
    return file_name


@app.route('/download/<file_name>', methods=['GET'])
@login_required
def download(file_name):
    return send_from_directory(DB_FOLDER, file_name)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            user = User.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                if user.is_admin:
                    return redirect('admin')
                return redirect('/')
            else:
                flash('Логин или пароль неверны!')
        else:
            flash('Заполните пустые текстовые поля!')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login and password and password2):
            flash('Пожалуйста, заполните все поля!')
        elif password != password2:
            flash('Повторный ввод пароля невереный!')
        elif User.query.filter_by(login=login).first():
            flash('Данный пользователь уже зарегистрирован!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, _roles=[Role.query.filter_by(name='participant').one()])
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/change_name/', methods=['POST'])
@login_required
def change_name():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    CREATORS[session['file_name']].change_atr_name(session['table_index'], index, val)
    return redirect(url_for('show_table'))


@app.route('/change_index/', methods=['POST'])
@login_required
def change_index():
    index = int(request.form.get('index'))
    val = int(request.form.get('val'))
    CREATORS[session['file_name']].change_atr_index(session['table_index'], index, val)
    return redirect(url_for('show_table'))


@app.route('/change_type/', methods=['POST'])
@login_required
def change_type():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    varchar_num = int(request.form.get('varchar'))
    CREATORS[session['file_name']].change_atr_type(session['table_index'], index, val, varchar_num)
    return redirect(url_for('show_table'))


@app.route('/change_constraint/', methods=['POST'])
@login_required
def change_constraint():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    CREATORS[session['file_name']].change_atr_constraint(session['table_index'], index, val)
    return redirect(url_for('show_table'))


@app.route('/change_fk_table/', methods=['POST'])
@login_required
def change_fk_table():
    index = int(request.form.get('index'))
    table_index = request.form.get('table_index')
    if table_index is None:
        return ''
    table_index = int(table_index)

    value = CREATORS[session['file_name']].tables[table_index].name
    CREATORS[session['file_name']].change_atr_foreign_key(session['table_index'], index, value, None)

    dict = CREATORS[session['file_name']].tables[table_index].attributes
    dis = request.form.get('dis')
    atr = CREATORS[session['file_name']].tables[session['table_index']].attributes[index]
    return render_template('Selector.html', index=index, atr=atr, dict=dict, disabled=dis)


@app.route('/change_fk_atr/', methods=['POST'])
@login_required
def change_fk_atr():
    index = request.form.get('index')
    if index is None:
        redirect(url_for('show_table'))
    index = int(index)
    value = request.form.get('val')
    CREATORS[session['file_name']].change_atr_foreign_key(session['table_index'], index, None, value)

    return redirect(url_for('show_table'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
