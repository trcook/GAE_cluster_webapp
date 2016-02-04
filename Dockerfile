# this is functionally a dockerized version of the image that gets rstudio and gcsfuse setup in docker. More changes in this file soon to make it more simplified and protable.


#! /bin/bash
FROM debian:jessie

RUN apt-get update
RUN	apt-get install -y r-base
RUN	apt-get install -y gdebi-core
RUN	mkdir /rstudio-install
RUN	cd /rstudio-install



RUN	apt-get install -y libcurl4-openssl-dev libssl-dev  libxml2-dev curl wget

RUN	apt-get install -y gdebi-core

WORKDIR ["/rstudio-install"]
RUN	wget -P /rstudio-install/ https://download2.rstudio.org/rstudio-server-0.99.491-amd64.deb
RUN	gdebi -n /rstudio-install/rstudio-server-0.99.491-amd64.deb

RUN	apt-get update
RUN	apt-get install -y apt-transport-https



ENV GCSFUSE_REPO gcsfuse-jessie
RUN	echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" >> /etc/apt/sources.list.d/gcsfuse.list
RUN	curl https://packages.cloud.google.com/apt/doc/apt-key.gpg |  apt-key add -

#RUN	apt-get purge lxc-docker*
#RUN	apt-get purge docker.io*
RUN	apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
RUN	echo deb https://apt.dockerproject.org/repo debian-jessie main >>  /etc/apt/sources.list.d/docker.list
RUN	apt-get update
RUN	apt-get install -y gcsfuse
RUN	apt-get install -y docker-engine

RUN	curl -Lo /usr/bin/rmate https://raw.githubusercontent.com/textmate/rmate/master/bin/rmate
RUN	chmod a+x /usr/bin/rmate
