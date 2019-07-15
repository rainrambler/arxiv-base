# arxiv/base

FROM centos:centos7

LABEL maintainer="arXiv <nextgen@arxiv.org>" \
  org.label-schema.schema-version="1.0" \
  org.label-schema.name="arXiv Base" \
  org.label-schema.description="Base image for arXiv NG applications" \
  org.label-schema.url="https://arxiv.github.io/arxiv-base" \
  org.label-schema.vcs-url="https://github.com/arxiv/arxiv-base" \
  org.label-schema.vendor="arXiv.org"

# Below we use && chaining and an embedded script in a single RUN
# command to keep image size and layer count to a minimum, while
# the embedded script will make 'docker build' fail fast
# if a package is missing.
#
RUN yum -y install epel-release \
  && yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
  && echo $'#!/bin/bash\n\
PKGS_TO_INSTALL=$(cat <<-END\n\
  ca-certificates\n\
  gcc\n\
  gcc-c++ \n\
  git\n\
  python36u\n\
  python36u-devel\n\
  which\n\
  wget\n\
  mariadb-devel\n\
END\n\
)\n\
for pkg in ${PKGS_TO_INSTALL}; do\n\
  # Stop executing if at least one package is not available:\n\
  yum info ${pkg} || {\n\
    echo "yum could not find package ${pkg}"\n\
    exit 1\n\
  }\n\
done\n\
yum -y install ${PKGS_TO_INSTALL}\n' >> /tmp/safe_yum.sh \
  && /bin/bash /tmp/safe_yum.sh \
  && yum clean all \
  && rm /tmp/safe_yum.sh

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python3.6 get-pip.py \
  && pip install -U pip pipenv uwsgi \
  && rm -rf ~/.cache/pip

ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    APPLICATION_ROOT="/"

LABEL version="0.15.9"

CMD /bin/bash
