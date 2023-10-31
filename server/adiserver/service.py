#!/usr/bin/env python3

'''
    Implementacion del servicio de blobs o paquetes de bytes
'''
import sqlite3

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
                users TEXT NOT NULL);''')

            self.conn.commit()  # Asegúrate de hacer commit después de la creación de la tabla
            print("Table created successfully")
        except Exception as e:
            print(f"Error al conectarse a la base de datos: {str(e)}")

    def create_blob(self, name, local_name, visibility, users):
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            cursor = self.conn.cursor()  # Obtenemos un cursor en lugar de abrir una nueva conexión
            cursor.execute("INSERT INTO blobs (name, local_name, visibility, users) VALUES (?, ?, ?, ?)",
                        (name, local_name, visibility, users))
            self.conn.commit()
            print("Record inserted successfully")
            last_insert_id = cursor.lastrowid  # Obtenemos el lastrowid a partir del cursor
            print(f"Last inserted ID: {last_insert_id}")
            return last_insert_id
        except Exception as e:
            print(f"Record insertion failed: {str(e)}")
            return None

    def update_blob(self, id, name, local_name, visibility, users):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute(f"UPDATE blobs SET name = '{name}', local_name = '{local_name}', visibility = '{visibility}', users = '{users}' WHERE id = {id}")
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
            conn.execute(f"DELETE FROM blobs WHERE id = {id}")
            conn.commit()
            print("Record deleted successfully")
        except:
            print("Record deletion failed")
        finally:
            if conn:
                conn.close()

    def change_visibility(self, blob_id, new_visibility):
    
        try:
            self.conn = sqlite3.connect(self.db_file)
            cursor = self.conn.cursor()
            cursor.execute("UPDATE blobs SET visibility = ? WHERE id = ?", (new_visibility, blob_id))
            self.conn.commit()
            print(f"El blob con ID {blob_id} ahora tiene visibilidad {new_visibility}")
        except Exception as e:
            print(f"Error al cambiar la visibilidad: {str(e)}")
    
    def get_user_blobs(self,user):
    
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, local_name, visibility, users FROM blobs")
            rows = cursor.fetchall()

            user_blobs = []
            for row in rows:
                blob_id, name, local_name, visibility, users = row
                users_list = users.split(",") if users else []
                if user in users_list:
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
            print("Record selected successfully")
            return cursor.fetchone()
        except:
            print("Record selection failed")
        finally:
            if conn:
                conn.close()

    def get_users(self, id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.execute(f"SELECT users FROM blobs WHERE id = {id}")
            print("Record selected successfully")
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
            print("Record updated successfully")
        except:
            print("Record update failed")
        finally:
            if conn:
                conn.close()
