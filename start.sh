#!/bin/bash

nombre_imagen="adidockerserver"

# Verificar si el contenedor ya está en ejecución
if docker ps | grep -q $nombre_imagen; then
    echo "El contenedor '$nombre_imagen' ya está en ejecución."
    exit 1
fi

# Ejecutar el comando docker run en modo demonio (-d) con --rm (el contenedor será autoeliminado cuando se detenga)
docker run -p 3002:3002 -d --rm $nombre_imagen


