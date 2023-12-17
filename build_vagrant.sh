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

      # Crear una nueva imagen qcow2 y copiar el contenido de la imagen de VirtualBox
      qemu-img create $qcow2_options $qcow2_image_name 10G
      sudo modprobe nbd max_part=16
      sudo qemu-nbd -c /dev/nbd0 $qcow2_image_name
      sudo dd if=output.box of=/dev/nbd0 bs=16M status=progress
      sudo qemu-nbd -d /dev/nbd0
      sudo modprobe -r nbd
      # Ejecutar qemu-img para convertir la imagen VDI de VirtualBox a QCOW2
      qemu-img convert -O $qcow2_options output.box "$PWD/$qcow2_image_name"

      echo "QCOW2 generado: $PWD/$qcow2_image_name"

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
