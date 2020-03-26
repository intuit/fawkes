mkdir -p downloads/
cd downloads
curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.0.0-linux-x86_64.tar.gz
tar -xvf elasticsearch-7.0.0-linux-x86_64.tar.gz
wget https://artifacts.elastic.co/downloads/kibana/kibana-7.0.0-darwin-x86_64.tar.gz
tar -xvf kibana-7.0.0-darwin-x86_64.tar.gz
