#License Agreements:
#   neopip is free for academic use
#   others must contact Shixiang Wang <wangshx@shanghaitech.edu.cn> or other authors
# Copyright @ 2019 Shixiang Wang

FROM ubuntu:latest
MAINTAINER Shixiang Wang, wangshx@shanghaitech.edu.cn
RUN apt update -y && apt upgrade -y &&  \
    apt install -y wget curl \
    unzip bzip2 git python3-dev python3-pip tree\
    tcsh gawk vim && \
    apt autoremove && apt clean && apt purge && rm -rf /tmp/* /var/tmp/*
RUN pip3 install pyyaml
ADD prepare.py utils.py config.yaml data/ /root/
WORKDIR /root
#ENV CONDA_EXE /public/data/.neopip/miniconda/bin/conda
RUN ["/bin/bash", "-c", "python3 prepare.py"]


## set up passwd in entrypoin.sh
#ENTRYPOINT ["bash", "/opt/config/entrypoint.sh"]
## share
#EXPOSE 8888
#VOLUME ["xxx"]
