#!/bin/bash

nombre_imagen="adidockerserver"

# Obtener el ID del contenedor en ejecución
container_id=$(docker ps -q --filter "ancestor=$nombre_imagen")

# Verificar si el contenedor está en ejecución
if [ -z "$container_id" ]; then
    echo "El contenedor '$nombre_imagen' no está en ejecución."
    exit 1
fi

# Detener el contenedor
docker stop $container_id
