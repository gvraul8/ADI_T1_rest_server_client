#!/bin/bash

while [[ $# -gt 0 ]]; do
  case "$1" in
    -q|--qcow2)
      # Lógica para construir QCOW2 utilizando qemu-img
      echo "Construyendo QCOW2..."
      
      # Nombre de la imagen QCOW2 que deseas generar
      qcow2_image_name="virtualizacion_image.qcow2"

      # Parámetros adicionales de configuración (ajusta según tus necesidades)
      qcow2_options="-f qcow2 -o preallocation=metadata"

      # Ejecutar qemu-img para convertir la imagen VDI de VirtualBox a QCOW2
      qemu-img convert -O $qcow2_options output.box $qcow2_image_name

      echo "QCOW2 generado: $qcow2_image_name"
      shift
      ;;
    *)
      # Default behavior for other options (VirtualBox image)
      echo "Construyendo la imagen de VirtualBox..."
      vagrant package --output output.box
      vagrant destroy -f
      vagrant box add my_box output.box --force
      shift
      ;;
  esac
done
