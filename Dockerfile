#License Agreements:
#   neopip is free for academic use
#   others must contact Shixiang Wang <wangshx@shanghaitech.edu.cn> or other authors
# Copyright @ 2019 Shixiang Wang

FROM ubuntu:latest
MAINTAINER Shixiang Wang, wangshx@shanghaitech.edu.cn
RUN apt update -y && apt upgrade -y &&  \
    apt install -y wget curl \
    unzip bzip2 git python3-dev tree\
    tcsh gawk vim && \
    apt autoremove && apt clean && apt purge && rm -rf /tmp/* /var/tmp/*
ADD prepare.py neoda.py neoda /root/
WORKDIR /root
ENV HOME_NEOPIP=/public
RUN mkdir /public && python prepare.py
# Clean conda environments
RUN . neoda activate --python3 && \
    conda clean -a -y && \
    apt autoremove && apt clean && apt purge && rm -rf /tmp/* /var/tmp/* && \
    . neoda activate && \
    conda clean -a -y && \
    apt autoremove && apt clean && apt purge && rm -rf /tmp/* /var/tmp/*


## set up passwd in entrypoin.sh
#ENTRYPOINT ["bash", "/opt/config/entrypoint.sh"]
## share
#EXPOSE 8888
#VOLUME ["xxx"]