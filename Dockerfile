FROM python:3.10-slim

WORKDIR /server

# Instalar las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./server /server
COPY ./auth_client /auth_client

# Instala setup.py
RUN pip install ../auth_client
RUN pip install .

# Expone por defecto el puerto externo TCP del servicio
ENV BLOB_SERVICE_PORT=3002
EXPOSE $BLOB_SERVICE_PORT/tcp

# Limita el acceso a una única CPU y 2GB de RAM
ENV CPU_LIMIT=1
ENV MEMORY_LIMIT=2g
ENV DEFAULT_AUTH_URL='http://192.168.18.93:3001'

# Configuración del volumen
ENV BLOB_STORAGE_FOLDER="$CWD/storage"
VOLUME ["$BLOB_STORAGE_FOLDER"]

# Comando para ejecutar la aplicación
#CMD adi_server -a http://192.168.18.93:3001
CMD adi_server -a "${DEFAULT_AUTH_URL}"
#CMD ["adi_server", "-a", "${DEFAULT_AUTH_URL}"]
#CMD echo ${DEFAULT_AUTH_URL}

#ENTRYPOINT ["tail", "-f", "/dev/null"]