import argparse
import cmd
import json
import requests
from flask import make_response, jsonify

from errors import BlobServiceError, Unauthorized

from typing import Union
from pathlib import Path

class Blob:
    """Blob class"""
    def __init__(self, blobId, authToken,serviceURL):
        self.blobId = blobId
        self.authToken = authToken
        self.serviceURL = serviceURL

    def __str__(self):
       return f"Blob ID: {self.blobId}\nAuth Token: {self.authToken}\nAccess URL: {self.accessURL}\nIs Private: {self.isPrivate}\nMD5: {self.md5}\nSHA256: {self.sha256}\nAllowed Users: {', '.join(self.allowedUsers)}"


    def addData(self, accessURL, allowedUsers, isPrivate, md5, sha256):
        """ Add data to blob """
        self.accessURL = accessURL
        self.allowedUsers = allowedUsers
        self.isPrivate = isPrivate
        self.md5 = md5
        self.sha256 = sha256


    def delete(self):
        """ Delete a blob """
        blob_service = BlobService(self.serviceURL, self.authToken)
        return blob_service.deleteBlob(self)

    def revokeUser(self, username):
        """ Delete a user from the access list """
        self.allowedUsers = self.allowedUsers[0].split(',')
        self.allowedUsers = [user.strip() for user in self.allowedUsers]

        if username in self.allowedUsers:
            self.allowedUsers.remove(username)
            print(f"User '{username}' has been revoked from the access list.")


    def setVisibility(self, visibility):
        """ Change blob visibility """
        visibility = visibility.lower()
        if visibility == "private":
            self.isPrivate = True
            print("Blob visibility set to private.")
        elif visibility == "public":
            self.isPrivate = False
            print("Blob visibility set to public.")
        else:
            raise BlobServiceError("Invalid visibility value. Valid values are 'private' and 'public'.")

    def allowUser(self, username):
        """ Add user to accesslist """
        if isinstance(self.allowedUsers, str):
            self.allowedUsers = self.allowedUsers.split(',')
        elif not isinstance(self.allowedUsers, list):
            self.allowedUsers = []

        if username not in self.allowedUsers:
            print(self.allowedUsers)
            self.allowedUsers.append(username)
            print(f"User '{username}' has been allowed access to the blob.")



    def dumpToFile(self, localFilename):
        """ Save a blob on local file """
        if localFilename:
            blob_service = BlobService(self.serviceURL, self.authToken)
            blob_data = blob_service.getBlob(self.accessURL)
            if blob_data:
                with open(localFilename, 'wb') as file:
                    file.write(blob_data)
                    print(f"Blob saved to local file: {localFilename}")
            else:
                print("Failed to retrieve blob data.")
        else:
            print("Local filename not provided.")

    def uploadFromFile(self, blobId, localFileName):
        """Upload content from file to blob.

        Args:
            blobId (str): Blob ID.
            localFileName (str): Local file name.

        Returns:
            Blob: The updated blob.
        """
        data_upload = {}
        try:
            with open(localFileName, 'r') as file:
                for linea in file:
                    # Convertir la línea a un diccionario
                    clave, valor = linea.strip().split(':', 1)
                    # Almacenar en el diccionario
                    data_upload[clave] = valor
            json_data = json.dumps(data_upload, indent=2)
            headers = {'USER-TOKEN': self.authToken}
            blob_service = BlobService(self.serviceURL, self.authToken)
            print(data_upload)
            print(self.serviceURL)
            print(blobId)
            print(headers)
            response = requests.put(f'{blob_service.serviceURL}/api/v1/blob/{blobId}', headers=headers, json=data_upload)

            if response.status_code == 204:
                print(f"Blob content uploaded successfully to blob ID {blobId}")
                return Blob(blobId, self.authToken)
            else:
                raise BlobServiceError(f"Failed to upload content to blob: {response.status_code}")
        except Exception as e:
            print(f"Error uploading content from file: {str(e)}")
            raise

class BlobService:
    def __init__(self, serviceURL, authToken=None):
        self.serviceURL = serviceURL
        self.authToken = authToken

    def createBlob(self, localFileName):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")
        datos = {}
        try:
            with open(localFileName, 'r') as file:
                for linea in file:
                    # Convertir la línea a un diccionario
                    clave, valor = linea.strip().split(':', 1)
                    # Almacenar en el diccionario
                    datos[clave] = valor
        except Exception as e:
            raise BlobServiceError(f"Failed to read file: {str(e)}")
     
        headers = {"USER-TOKEN": self.authToken}
        response = requests.post(f"{self.serviceURL}/api/v1/blob", headers=headers, json=datos)

        if response.status_code == 201:
            blob_data = response.json()
            return Blob(blob_data["BlobId"], self.authToken)
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        else:
            print(response.status_code)
            raise BlobServiceError("Failed to create blob")

    def getMyBlobs(self):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        response = requests.get(f"{self.serviceURL}/api/v1/blob/myblobs", headers=headers)

        if response.status_code == 200:
            blobs_data = response.json()
            return blobs_data
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        else:
            raise BlobServiceError("Failed to get blobs")

    def getBlob(self, blobId):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        response = requests.get(f"{self.serviceURL}/api/v1/blob/{blobId}", headers=headers)

        if response.status_code == 200:
            blob_data = response.json()

            blob = Blob(blob_data['id'], self.authToken)
            responseMD5 = requests.get(f"{self.serviceURL}/api/v1/blob/{blobId}/hash?type=MD5", headers=headers)
            responseSHA256 = requests.get(f"{self.serviceURL}/api/v1/blob/{blobId}/hash?type=SHA256", headers=headers)

            if responseMD5.status_code == 200 and responseSHA256.status_code == 200:
                md5_hash = responseMD5.text
                sha256_hash = responseSHA256.text
            else:
                if responseMD5.status_code != 200:
                    print(f"Error obteniendo el hash MD5: {responseMD5.status_code}")
                if responseSHA256.status_code != 200:
                    print(f"Error obteniendo el hash SHA-256: {responseSHA256.status_code}")

            accessURL = "/api/v1/blob/" + blobId

            blob.addData(accessURL, blob_data["users"], blob_data["visibility"], md5_hash, sha256_hash)
            return blob
        elif response.status_code == 404:
            return make_response('Blob not found', 404)
        else:
            raise BlobServiceError("Failed to get blob")

    def deleteBlob(self, blobId):
        print("Deleting blob...")
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        response = requests.delete(f"{self.serviceURL}/api/v1/blob/{blobId}", headers=headers)

        if response.status_code == 204:
                print("Blob deleted successfully")
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        else:
            raise BlobServiceError("Failed to delete blob")

    def updateVisibility(self, blobId, visibility):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        blob = Blob(blobId, self.authToken)
        blob.setVisibility(visibility)

        visibility = visibility.lower()
        if visibility == "private":
            visibility = "False"
        elif visibility == "public":
            visibility = "True"

        data = {"visibility": visibility}

        response = requests.put(f"{self.serviceURL}/api/v1/blob/{blobId}/visibility", headers=headers, json=data)

        if response.status_code == 204:
            print("Blob visibility updated successfully")
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        elif response.status_code == 404:
            raise BlobServiceError("Blob not found")
        else:
            raise BlobServiceError("Failed to update blob visibility")

    def updateACL(self, blobId, username, type):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        blob = self.getBlob(blobId)

        print(blob.allowedUsers)

        # Si el tipo es 1 es para allow user, si no es para revoke user
        if type == 1:
            blob.allowUser(username)
        else:
            blob.revokeUser(username)

        data = {"users": blob.allowedUsers}
        print(data)

        response = requests.put(f"{self.serviceURL}/api/v1/blob/{blobId}/acl", headers=headers, json=data)

        if response.status_code == 204:
            print("Blob ACL updated successfully")
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        elif response.status_code == 404:
            raise BlobServiceError("Blob not found")
        else:
            raise BlobServiceError("Failed to update blob ACL")

    def getBlobACL(self, blobId):
        if not self.authToken:
            raise Unauthorized("Authentication token is required for this operation.")

        headers = {"USER-TOKEN": self.authToken}

        response = requests.get(f"{self.serviceURL}/api/v1/blob/{blobId}/acl", headers=headers)

        if response.status_code == 200:
            blob_data = response.json()
            return blob_data
        elif response.status_code == 401:
            raise Unauthorized("Unauthorized")
        elif response.status_code == 404:
            raise BlobServiceError("Blob not found")
        else:
            raise BlobServiceError("Failed to get blob ACL")

class ClientCMD(cmd.Cmd):

    def __init__(self, serviceURL, authURL, authToken):
        super().__init__()
        self.blob_service = BlobService(serviceURL, authToken)
        self.blob = Blob(None, authToken,serviceURL)
        self.serviceURL = serviceURL
        self.authURL = authURL
        self.authToken = authToken
        self.intro = "Bienvenido a la Shell Blob. Escribe 'help' o '?' para listar los comandos disponibles."
        self.prompt = "(Blob) >>  "

    def do_create_blob(self, args):
        """Crea un nuevo blob."""
        if not args:
            print("Uso incorrecto. Debes proporcionar <localFileName>")
            return
        try:
            self.blob = self.blob_service.createBlob(args)
            print("Blob creado correctamente con id: " + str(self.blob.blobId))
        except Exception as e:
            print("Error al crear el blob: " + str(e))

    def do_get_blob_by_id(self, args):
        """Obtiene un blob."""
        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId>")
            return
        try:
            self.blob = self.blob_service.getBlob(args)
            print("Blob obtenido correctamente con id: " + str(self.blob.__str__()))
        except Exception as e:
            print("Error al obtener el blob: " + str(e))

    def do_get_my_blobs(self, args):
        """Obtiene los blobs del usuario."""
        try:
            print("Obteniendo blobs...")
            blobs = self.blob_service.getMyBlobs()
            for blob in blobs:
                print(blob)
                if len(blobs) > 1:
                    print(" , ")
        except Exception as e:
            print("Error al obtener los blobs: " + str(e))

    def do_delete_blob(self, args):
        """Elimina el blob actual."""
        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId>")
            return

        try:
            self.blob_service.deleteBlob(args)
            print("Blob eliminado correctamente.")
        except Exception as e:
            print("Error al eliminar el blob: " + str(e))

    def do_set_visibility(self, args):
        """Establece la visibilidad del blob (privado o público)."""
        if not self.blob:
            print("No se ha creado un blob. Use 'create_blob' para crear un blob primero.")
            return
        elif not args:
            print("Uso incorrecto. Debes proporcionar <blobId> <visibility>")
            return

        args = args.split(" ")
        try:
            self.blob = self.blob_service.getBlob(args[0])
            self.blob_service.updateVisibility(args[0], args[1])
        except Exception as e:
            print("Error al establecer la visibilidad: " + str(e))

    def do_allow_user(self, args):
        """Permite a un usuario acceder al blob."""
        if not self.blob:
            print("No se ha creado un blob. Use 'create_blob' para crear un blob primero.")
            return

        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId> <username>.")
            return

        args = args.split(" ")
        try:
            self.blob = self.blob_service.getBlob(args[0])
            self.blob_service.updateACL(args[0], args[1], 1) # 1 porque es para allow user

        except Exception as e:
            print("Error al modificar la ACL: " + str(e))

    def do_revoke_user(self, args):
        """Permite a un usuario acceder al blob."""
        if not self.blob:
            print("No se ha creado un blob. Use 'create_blob' para crear un blob primero.")
            return

        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId> <username>.")
            return

        args = args.split(" ")
        try:
            self.blob = self.blob_service.getBlob(args[0])
            self.blob_service.updateACL(args[0], args[1], 0) # 0 porque es para revoke user
        except Exception as e:
            print("Error al modificar la ACL: " + str(e))

    def do_get_blob_acl(self, args):
        """Obtiene la ACL del blob."""
        if not self.blob:
            print("No se ha creado un blob. Use 'create_blob' para crear un blob primero.")
            return

        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId>.")
            return

        try:
            acl = self.blob_service.getBlobACL(args)
            print("ACL del blob " +str(args) +": " + str(acl))
        except Exception as e:
            print("Error al obtener la ACL: " + str(e))
    
    def do_exit(self, args):
        """Sale de la aplicación."""
        print("Saliendo de la aplicación...")
        return True
    
    def do_uploadFromFile(self, args):
        """Upload content from file to blob.

        Usage: uploadFromFile <blobId> <localFileName>

        Example: uploadFromFile 1234567890 my_file.txt
        """

        if not args:
            print("Uso incorrecto. Debes proporcionar <blobId> <localFileName>")
            return

        args = args.split(" ")

        try:
            #self.blob = self.blob_service.getBlob(args[0])
            self.blob = self.blob.uploadFromFile(args[0], args[1])
            print("El contenido del archivo se ha subido correctamente al blob")
        except Exception as e:
            print("Error al subir el contenido del archivo: " + str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente Blob")
    parser.add_argument("serviceURL", type=str, help="URL del servicio Blob")
    parser.add_argument("authURL", type=str, help="URL del servicio de autenticación")
    parser.add_argument("userToken", type=str, help="Token de usuario")

    args = parser.parse_args()

    ClientCMD(args.serviceURL, args.authURL, args.userToken).cmdloop()
