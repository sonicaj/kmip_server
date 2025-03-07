FROM python:3.11.9

ENV PYTHONUNBUFFERED 1
ENV WORK_DIR /app
RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}

EXPOSE 5696
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y build-essential --fix-missing

# install our app requirements
ADD requirements.txt ${WORK_DIR}
RUN pip install --disable-pip-version-check --exists-action w -r requirements.txt && \
    rm -rf ~/.cache/pip /tmp/pip-build-root

# clean up a bit
RUN apt-get -y purge libpq-dev build-essential && \
    apt-get -y autoremove && \
    apt-get -y clean

ADD . ${WORK_DIR}/
