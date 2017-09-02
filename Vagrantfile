Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"
  config.vm.provider "virtualbox" do |v|
    v.name = "interview_manager"
  end
  config.vm.network "forwarded_port", host_ip: "127.0.0.1", guest: 8080, host: 8080
  config.vm.synced_folder "./", "/home/vagrant/im", type: "rsync"
  config.vm.provision "shell", privileged: false, path: "./setup.sh"
end
