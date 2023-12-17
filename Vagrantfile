# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANT_CONF = {
  storage_folder: ENV['BLOB_STORAGE_FOLDER'] || '/home/raul14m/Desktop/Blob_storage',
  service_port: ENV['BLOB_SERVICE_PORT'] || 3002
}

ENV['BLOB_STORAGE_FOLDER'] ||= '/home/raul14m/Desktop/Blob_storage'
ENV['BLOB_SERVICE_PORT'] ||= '3002'
# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.network "forwarded_port", guest: 3002, host: ENV["BLOB_SERVICE_PORT"] || 3002
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 1
  end
  config.vm.synced_folder ".", "/vagrant", disabled: false

  config.vm.provision "shell", path: "bootstrap.sh"


  config.vm.provision "shell" do |shell|
    shell.inline = <<-SHELL
      export BLOB_STORAGE_FOLDER='/home/raul14m/Desktop/Blob_storage'
      export BLOB_SERVICE_PORT=3002
      echo 'Instalando dependencias...'
      sudo apt-get update
      sudo apt-get install -y python3-pip
      pip3 install --upgrade pip
      pip3 install -r /vagrant/requirements.txt
      cd /vagrant/auth_client
      pip install .
      cd ../server
      pip install .
      cd /auth_service
      pip install .
      cd ../server
    SHELL
  end
  # Configuración del almacenamiento
  if ENV['BLOB_STORAGE_FOLDER']
    config.vm.provision "shell", inline: "echo 'Usando carpeta compartida.'"
    config.vm.synced_folder VAGRANT_CONF[:storage_folder], '/home/raul14m/Desktop/Blob_storagee'
  else
    # Configuración para un disco aparte compatible con VirtualBox
    config.vm.provision "shell", inline: "echo 'Usando disco duro.'"
    config.vm.disk :disk, size: 10, primary: true

    # Puedes especificar el sistema de archivos, por ejemplo, ext4
    config.vm.provision "shell", inline: <<-SHELL
      echo 'Creando sistema de archivos ext4 en el disco.'
      mkfs.ext4 /dev/sdb
    SHELL

  end
  #config.vm.network "forwarded_port", guest: 80, host: 8000
  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Disable the default share of the current code directory. Doing this
  # provides improved isolation between the vagrant box and your host
  # by making sure your Vagrantfile isn't accessable to the vagrant box.
  # If you use this you may want to enable additional shared subfolders as
  # shown above.
  # config.vm.synced_folder ".", "/vagrant", disabled: true

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision "shell", inline: <<-SHELL
  #   apt-get update
  #   apt-get install -y apache2
  # SHELL
end
