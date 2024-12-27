"""
Класс для работы с базой данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import insert, update, delete, text, select

from supportFunctions import resultproxy_to_dict, result_query_to_dict, list_to_dict 

# from config.config import tr
 
from contextlib import contextmanager
# from core.base1 import Base1
# from core.base2 import Base2  
from models import Base, Users

from sqlalchemy import create_engine, MetaData
import os
from config import config
import base64

class SQLDataBase():

    def __init__(self):
        # self.trace = tr
        self.engine = create_engine(config.DATABASE_URI+"spbot", future=True)
        self.create_session()  
        
        for model, modelname in zip(config.SUBJECT_NAME_TO_CLASS.values(), config.SUBJECT_NAME_TO_CLASS.keys()):
            questions = self.select_all_params_from_table_by_column_in_dict(str(model.__name__), model, 'is_approved', False)
            questions_not_empty = self.select_all_params_from_table_by_column_in_dict(str(model.__name__), model, 'is_empty', False)
            for q in questions:
                if q in questions_not_empty:
                    config.ANSWERS_FOR_MODERATION.append([q['id'], modelname])

    def db_create(self):
        '''
        Метод для создания таблиц и базы данных
        '''
        Base.metadata.create_all(self.engine)

    def recreate_database(self):

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        #Создание сессии, через которую мапяться объекты
        self.session = sessionmaker(bind=self.engine)()
        
    def create_table(self, tablename):
        request_str = text("CREATE TABLE "+tablename)
        s = self.session.execute(request_str)
        #s = self.session.query(dbClass)
        # result_of_query = resultproxy_to_dict(s)
        # return result_of_query
        return True

    def encrypt_dict_user_data(self, classModel, data: dict):
        # if classModel == Users and ("wb_token" in data.keys()):
        #     data["wb_token"] = self.cipher_suite.encrypt(str(data["wb_token"]).encode('utf-8'))
        return data
    
    def decrypt_dict_user_data(self, classModel, data: dict):
        # if classModel == Users and ("wb_token" in data.keys()):
        #     print(data["wb_token"])
        #     data["wb_token"] = str(self.cipher_suite.decrypt(data["wb_token"], 'utf-8').decode())
        return data

    def databaseAddCommit(self,type_object):
        self.session.add(type_object)
        self.session.commit()

    def databaseAddCommitMultiply(self,classModel, type_objects):
        
        with self.engine.connect() as conn:
            type_objects = self.encrypt_dict_user_data(Users, type_objects)
            result = conn.execute(
                insert(classModel),
                        type_objects)
            conn.commit()
        return result

    def databaseUpdateCommitMultiply(self,classModel, type_objects):
        try:
            type_objects = self.encrypt_dict_user_data(Users, type_objects)
            for item in type_objects:
                self.databaseUpdateEntity(classModel, item["id"], item["updateDict"])
            self.session.commit()
            result = True
        except:
            result = False
        return result

    def databaseUpdateEntity(self, dbClass, id, updateDict):
        self.session.query(dbClass).filter(dbClass.id == id).update(
            self.encrypt_dict_user_data(dbClass, updateDict))
        self.session.commit()
        return True

    def databaseDeleteCommitMultiply(self,classModel, type_objects):
        with self.engine.connect() as conn:
            result = conn.execute(
                delete(classModel),
                        type_objects)
            conn.commit()
        return result

    def databaseDeleteCommitCycle(self,classModel, type_objects):
        try:
            for item in type_objects:
                self.session.query(classModel).filter(classModel.id == item["id"]).delete()
            self.session.commit()
            return True
        except Exception as error:
            # tr.save_msg("!"+str(error))
            return False

    def databaseSearchByID(self, classModel, id):
        s = self.session.query(classModel).filter(classModel.id == id)
        result = result_query_to_dict(s)
        if len(result) == 0:
            return None
        else:
            return self.decrypt_dict_user_data(Users, result[0])
        
    def databaseSearchByUsername(self, classModel, username):
        s = self.session.query(classModel).filter(classModel.username == username)
        result = result_query_to_dict(s)
        if len(result) == 0:
            return None
        else:
            return self.decrypt_dict_user_data(Users, result[0])
    
    def databaseUpdateCommitContainers(self, dbClass, id, lastOperationID):
        self.session.query(dbClass).filter(dbClass.id == id).update(
            {'lastoperationid': lastOperationID})
        self.session.commit()
        
    @contextmanager
    def session_scope(self):
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as error:
            # tr.save_msg("!"+str(error))
            session.rollback()
            raise
        finally:
            session.close()

    def sessionCloseAll(self):
        session = self.session
        session.close_all()

    def select_all_params_in_table(self,name, dbClass):
        # Функция для подачи запроса
        request_str = text("SELECT * \
                           FROM \
                           " + str(name))
        s = self.session.query(dbClass)
        #s = self.session.execute(request_str)
        #result_of_query = resultproxy_to_dict(s)
        result_of_query = result_query_to_dict(s)
        return result_of_query

    def select_all_params_from_table_in_dict(self, dbClass):
        try:
            s = self.session.query(dbClass)
            result_of_query = result_query_to_dict(s)
            result_dict = list_to_dict(result_of_query)
            vals = list(result_dict.values())
            for val_num in range(len(vals)):
                vals[val_num] = self.decrypt_dict_user_data(Users, vals[val_num])
        except Exception as error:
            print(error)
            # tr.save_msg("!"+str(error))
            self.session.rollback()
            vals = []
        return vals

    def select_all_params_from_table_by_column_in_dict(self, name, dbClass, nameColumn, valueColumn):
        # Функция для подачи запроса
        request_str =  text("SELECT * \
                              FROM \
                              " + str(name)+ "\
                           WHERE \
                              " + str(nameColumn)+ " \
                              = '" + str(valueColumn) + "'")
        try:
            s = self.session.execute(request_str)
            #s = self.session.query(dbClass)
            result_of_query = resultproxy_to_dict(s)
        except:
            self.session.rollback()
            result_of_query = []
        #result_dict = list_to_dict(result_of_query)
        return result_of_query

    def select_all_params_in_table_by_ID(self,name, ID, dbClass):
        # Функция для подачи запроса
        request_str = text("SELECT * \
                           FROM \
                           " + str(name) + "\
                           WHERE ID = " + str(ID))
        s = self.session.query(dbClass)
        #s = self.session.execute(request_str)
        #result_of_query = resultproxy_to_dict(s)
        result_of_query = result_query_to_dict(s)
        return result_of_query

    def select_one_params_in_table(self, name, name_column):
        # Функция для подачи запроса
        request_str = text("SELECT " + str(name_column) + " \
                              FROM \
                              " + str(name) +" \
                                WHERE type_id = 1")
        s = self.session.execute(request_str)
        result_of_query = resultproxy_to_dict(s)
        return result_of_query

    def request_delete_of_measured(self,name):
        #Запрос на удаление всего из таблицы measure
        request_str = text("DELETE FROM " + str(name) +" \
                           WHERE type_id = 1")
        self.session.execute(request_str)

    def request_count_of_blades(self, name):
        # Запрос на подсчет количества лопаток в базе данных
        request_str = text("SELECT count(part_id) AS Количество \
                        FROM " + str(name))
        s = self.session.execute(request_str)
        result_of_query = resultproxy_to_dict(s)
        return result_of_query
    
    def request_all_tables(self):
        request_str = text("SELECT table_name FROM information_schema. tables WHERE table_schema = 'spbot'")
        s = self.session.execute(request_str)
        result_of_query = resultproxy_to_dict(s)
        return result_of_query

    def request_update_of_numbers(self, name, numbers):
        #Запрос на обновление данных в таблице

        k = 1
        for i in numbers:
            request_str = text("UPDATE " + str(name) + " \
                            SET serial_number = " + str(i) + "\
                            WHERE part_id = " + str(k))
            k += 1
            self.session.execute(request_str)
            self.session.commit()
            
database = SQLDataBase()