from exel_to_database import db, User


def create_users():
    db.session.add(Role(name="admin",
                        description="Администратор управляет всеми учетными записями на сайте и файлами, которые хранятся в базе данных."))
    db.session.add(Role(name="participant",
                        description=" Участник может преобразовывать файлы эксель в бд, а также хранить файлы бд на сервере."))
    #db.session.add(User(login='Sergey', password='ser3', _roles=[Role.query.filter_by(name='participant').one()]))
    #db.session.add(User(login='Petr', password='pet2', _roles=[Role.query.filter_by(name='participant').one()]))
    #db.session.add(User(login='admin', password='admin1', _roles=Role.query.all()))
    db.session.commit()


# def relationship_test():
#     user = User.query.filter_by(login='Sergey').one()
#     user._files = [File(name='user_test.db', path='../DBs/users_test.db')]
#     db.session.commit()
from exel_to_database.models import File, Role


def show_bd():
    print(User.query.all())
    print(Role.query.all())


if __name__ == '__main__':

