#!/usr/bin/env python3

'''
    Implementacion del servicio de blobs o paquetes de bytes
'''
import sqlite3
import uuid

class BlobDB:
    '''
        Controla la base de datos persistente del servicio de blobs
    '''

    def __init__(self, db_file):
        self.db_file = db_file
        try:
            self.conn = sqlite3.connect(db_file)
            print("Opened database successfully")
            self.conn.execute('''CREATE TABLE IF NOT EXISTS blobs
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                local_name TEXT NOT NULL,
                visibility TEXT NOT NULL,
                users TEXT NOT NULL,
                owner TEXT NOT NULL);''')

            self.conn.commit()  # Asegúrate de hacer commit después de la creación de la tabla
            print("Table created successfully") 
        except Exception as e:
            print(f"Error al conectarse a la base de datos: {str(e)}")

    def create_blob(self, name, local_name, visibility, users,owner_blob):
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            cursor = self.conn.cursor()  # Obtenemos un cursor en lugar de abrir una nueva conexión
            cursor.execute("INSERT INTO blobs (name, local_name, visibility, users, owner) VALUES (?, ?, ?, ?, ?)",
                        (name, local_name, visibility, users,owner_blob))
            self.conn.commit()
            last_insert_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            return last_insert_id
        except Exception as e:
            print(f"Record insertion failed: {str(e)}")
            return None

    def blobOwner(self, blobId):

        try:
            self.conn = sqlite3.connect(self.db_file)
            cursor = self.conn.cursor()
            cursor.execute("SELECT owner FROM blobs WHERE id = ?", (blobId,))
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error al obtener el owner del blob: {str(e)}")
            return None
        
    def getVisibilityBlob(self, blobId):
            
        try:
            self.conn = sqlite3.connect(self.db_file)
            cursor = self.conn.cursor()
            cursor.execute("SELECT visibility FROM blobs WHERE id = ?", (blobId,))
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error al obtener la visibilidad del blob: {str(e)}")
            return None
        
    def update_blob(self, id, name, local_name, visibility, users):
        conn = None
        try:
            users_str = ', '.join(users)
            conn = sqlite3.connect(self.db_file)
            conn.execute(f"UPDATE blobs SET name = '{name}', local_name = '{local_name}', visibility = '{visibility}', users = '{users_str}' WHERE id = {id}")
            conn.commit()
            print("Record updated successfully")
        except:
            print("Record update failed")
        finally:
            if conn:
                conn.close()

    def delete_blob(self, id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.execute(f"SELECT * FROM blobs WHERE id = {id}")
            if cursor.fetchone() is not None:
                conn.execute(f"DELETE FROM blobs WHERE id = {id}")
                conn.commit()
                print("Record deleted successfully")
            else:
                print("Record with ID {} not found".format(id))
        except sqlite3.Error as e:
            print("Record deletion failed:", str(e))
        finally:
            if conn:
                conn.close()

    def change_visibility(self, blob_id, new_visibility):
    
        try:
            self.conn = sqlite3.connect(self.db_file)
            cursor = self.conn.cursor()
            cursor.execute("UPDATE blobs SET visibility = ? WHERE id = ?", (new_visibility, blob_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error al cambiar la visibilidad: {str(e)}")
    
    def get_blobs_by_user(self,user):
    
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, local_name, visibility, users FROM blobs WHERE owner = ?", (user,))

            rows = cursor.fetchall()

            user_blobs = []
            for row in rows:
                blob_id, name, local_name, visibility, users = row
                users_list = users.split(",")
                user_blobs.append({
                    "id": blob_id,
                    "name": name,
                    "local_name": local_name,
                    "visibility": visibility,
                    "users": users_list
                })
            return user_blobs
        
        except Exception as e:
            print(f"Error al obtener los blobs del usuario: {str(e)}")
            return []

    def get_blob(self, id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.execute(f"SELECT * FROM blobs WHERE id = {id}")
            row = cursor.fetchone()
            if row is not None:
                print("Record selected successfully")
                return row
            else:
                print("Record with ID {} not found".format(id))
                return None  # Retornar None para indicar que el registro no existe
        except sqlite3.Error as e:
            print("Record selection failed:", str(e))
            return None
        finally:
            if conn:
                conn.close()

    def get_users(self, id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.execute(f"SELECT users FROM blobs WHERE id = {id}")
            return cursor.fetchone()
        except:
            print("Record selection failed")
        finally:
            if conn:
                conn.close()

    def delete_user(self,blobId,user_to_remove_permission):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.execute(f"SELECT users FROM blobs WHERE id = {blobId}")
            users = cursor.fetchone()[0]
            users_list = users.split(",")
            users_list.remove(user_to_remove_permission)
            users = ",".join(users_list)
            conn.execute(f"UPDATE blobs SET users = '{users}' WHERE id = {blobId}")
            conn.commit()
        except:
            print("Record update failed")
        finally:
            if conn:
                conn.close()
