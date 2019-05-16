#License Agreements:
#   neopip is free for academic use
#   others must contact Shixiang Wang <wangshx@shanghaitech.edu.cn> or other authors
# Copyright @ 2019 Shixiang Wang

FROM ubuntu:latest
MAINTAINER Shixiang Wang, wangshx@shanghaitech.edu.cn
RUN apt update -y && apt upgrade -y &&  \
    apt install -y wget curl \
    unzip bzip2 git python3-dev tree\
    tcsh gawk vim\
    net-tools iputils-ping apt-transport-https openssh-server \
    apt-utils gdebi-core tmux \
    htop supervisor xclip cmake sudo \
    libapparmor1 libcurl4-openssl-dev libxml2 libxml2-dev libssl-dev libncurses5-dev libncursesw5-dev libjansson-dev \
    build-essential gfortran libcairo2-dev libxt-dev automake bash-completion \
    libapparmor1 libedit2 libc6 psmisc rrdtool libzmq3-dev libtool software-properties-common \
    bioperl libdbi-perl python-dev \ 
    locales && locale-gen en_US.UTF-8 && \
    cpan -i Try::Tiny && \
    add-apt-repository ppa:jonathonf/vim -y && \
    apt update -y &&  \
    apt install -y vim && \
    apt autoremove && apt clean && apt purge && rm -rf /tmp/* /var/tmp/* /root/.cpan/*


## set up passwd in entrypoin.sh
ENTRYPOINT ["bash", "/opt/config/entrypoint.sh"]
## share
EXPOSE 8888
VOLUME ["xxx"]