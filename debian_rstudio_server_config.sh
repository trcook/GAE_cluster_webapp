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



sudo useradd -m ruser
echo 'ruser:12345'|sudo chpasswd

sudo usermod -a -G sudoers ruser
sudo /bin/sh -c 'echo "ruser ALL=NOPASSWD: ALL">>/etc/sudoers'



sudo rstudio-server start

# INSTANCE_NAME=gcloud compute instances get-metadata hostname
# export INSTANCE_NAME=gcloud compute instances get-metadata hostname


# NAME=$(hostname)

# ZONE=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google"|cut -d/ -f4)

sudo gcloud compute instances add-metadata $(hostname) \
  --metadata rstudioready=brue --zone $(curl "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google"|cut -d/ -f4)


# start the rstudio server
