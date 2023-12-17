#!/bin/bash

# Verifica si se proporcionó la opción --qcow2
if [[ "$1" == "--qcow2" ]]; then
  # Lógica para ejecutar la imagen QCOW2
  echo "Ejecutando la imagen QCOW2..."
  qcow2_image_name="virtualizacion_image.qcow2"
  #Utilizando quemu para ejecutar la imagen
  qemu-system-x86_64 -drive file=$qcow2_image_name,format=qcow2
else
  # Comportamiento predeterminado para otras opciones (por ejemplo, VirtualBox)
  echo "Ejecutando la imagen de VirtualBox..."
  vagrant ssh -c "cd /vagrant/server/auth_service-main && pip install . && nohup /vagrant/server/auth_service-main/auth_service > auth_service.log 2>&1 &"
  vagrant up
  vagrant ssh -c "cd /vagrant/ && pip install flask && cd /vagrant/auth_client && pip install . && cd /vagrant/server/auth_service-main && pip install . && cd /vagrant/server && pip install . && cd /vagrant/server && adi_server -a http://127.0.0.1:3001 "
fi
