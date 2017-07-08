$script = <<SCRIPT
   ES_VERSION=2.4.2
   ROOT_PATH="/home/vagrant"

   sudo apt-get update && sudo apt-get install unzip openjdk-7-jre -y

   if [ ! -d $ROOT_PATH/elasticsearch-$ES_VERSION ]; then
       cd $ROOT_PATH && wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-$ES_VERSION.zip
       unzip $ROOT_PATH/elasticsearch-$ES_VERSION.zip
   fi

   $ROOT_PATH/elasticsearch-$ES_VERSION/bin/elasticsearch -d --cluster.name=test --transport.tcp.port=9300 --http.port=9200 --network.bind_host=0.0.0.0 --script.inline=true --discovery.zen.ping.unicast.hosts="localhost:9300,localhost:9301"
   $ROOT_PATH/elasticsearch-$ES_VERSION/bin/elasticsearch -d --cluster.name=test --transport.tcp.port=9301 --http.port=9201 --network.bind_host=0.0.0.0 --script.inline=true --discovery.zen.ping.unicast.hosts="localhost:9300,localhost:9301"
SCRIPT


Vagrant.configure('2') do |config|
  config.vm.box = 'ubuntu/trusty64'
  config.vm.hostname = 'elasticsearch'
  config.vm.provision "shell", inline: $script, privileged: false
  config.vm.network "forwarded_port", guest: 9200, host: 9210
  config.vm.network "forwarded_port", guest: 9201, host: 9211
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
  end
end
