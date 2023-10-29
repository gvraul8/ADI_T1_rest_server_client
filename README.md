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

### Lanzar el servidor
```bash
adi_server
```
