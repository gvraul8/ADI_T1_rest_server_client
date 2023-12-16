# ADI_T1_rest_server_client


## Desarrollo
### Crear entorno virtual
```bash
python3 -m venv adi
source adi/bin/activate
```

### Generar requirements.txt
```bash
pip freeze > requirements.txt
```


## Lanzar el proyecto
### Activar el entorno virtual
```bash
source adi/bin/activate
```


### Instalar las dependencias en auth_client
```bash
cd auth_client
pip install .
```


### Instalar las dependencias en el servidor
```bash
cd server
pip install .
```


### Instalar flask 
```bash
cd server
pip install flask
```


### Lanzar el auth_service
```bash
cd auth_service-main
auth_service
```


### Lanzar el servidor
```bash
adi_server
```

#### Podemos lanzar el servidor con configuraciones personalizadas: 
	- Un puerto diferente al de por defecto (3002)
```bash
adi_server -p <port>
```


	- Direccion de escucha diferente a la de por defecto (0.0.0.0)
```bash
adi_server -l <listening>
```

	- Base de datos diferente a la de por defecto (blob.db)
```bash
adi_server -d <db>
```

	- URL de auth_service diferente a la de por defecto (http://127.0.0.1:3001)
```bash
adi_server -a <url auth_service
```

### Creamos un usuario y hacemos login. Para ello podemos usar postman o el cliente del servicio de autenticación.

 - crear usuario 
 	-	PUT http://127.0.0.1:3001/v1/user/username
	-	Header: 'ADMIN-TOKEN': 'admin token'
	-	Body: JSON: {"hash-pass": "password"}

  - login 
	-	POST http://127.0.0.1:3001/v1/user/login
	-	Header: 'ADMIN-TOKEN': 'admin token'
	-	Body: JSON: {"hash-pass": "password", "user": "user name"}.

	Al hacer login nos devolverá un user_token, que se lo deberemos pasar al cliente


### Lanzamos el cliente, pasandole serviceURL, authURL y userToken
```bash
cd client
python3 client.py <serviceURL> <authURL> <userToken> 
```

Escribimos help y podemos ver las opciones que podemos realizar



## VIRTUALIZACIÓN CON DOCKER

### Construir imagen de Docker
```bash
./build.sh
```

### Iniciar contenedor
```bash
./start.sh
```

### Parar contenedor
```bash
./stop.sh
```
