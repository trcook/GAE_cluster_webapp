#! /bin/bash

sudo apt-get update
sudo apt-get install -y r-base

sudo apt-get install -y gdebi-core
sudo mkdir /rstudio-install
sudo cd /rstudio-install

sudo wget -P /rstudio-install/ https://download2.rstudio.org/rstudio-server-0.99.491-amd64.deb

sudo gdebi -n /rstudio-install/rstudio-server-0.99.491-amd64.deb


# install r-sepcific libs:
sudo apt-get install -y libcurl4-openssl-dev libssl-dev  libxml2-dev

# install gcsfuse:
# from: https://github.com/GoogleCloudPlatform/gcsfuse/blob/master/docs/installing.md
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -



sudo apt-get update
sudo apt-get install gcsfuse