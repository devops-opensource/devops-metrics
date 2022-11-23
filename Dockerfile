FROM python:3.10

LABEL authors="devops-opensource"

ARG APP_NAME=devops-metrics
ENV APP_NAME=${APP_NAME}

# Guidelines here: https://github.com/mozilla-services/Dockerflow/blob/master/docs/building-container.md
ARG USER_ID="10001"
ARG GROUP_ID="app"
ARG HOME="/app"

ENV HOME=${HOME}
RUN groupadd --gid ${USER_ID} ${GROUP_ID} && \
    useradd --create-home --uid ${USER_ID} --gid ${GROUP_ID} --home-dir /app ${GROUP_ID}

# List packages here
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        file        \
        gcc         \
        git         \
        libwww-perl  \
        default-mysql-client \ 
        libmariadb-dev-compat && \
    apt-get autoremove -y && \
    apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

WORKDIR ${HOME}

ADD . ${APP_NAME}   
ENV PATH $PATH:${HOME}/${APP_NAME}/bin

WORKDIR ${HOME}/${APP_NAME}

RUN pip install -r requirements/dev_requirements.txt
RUN pip install _submodules/splunk --upgrade

# Drop root and change ownership of the application folder to the user
RUN chown -R ${USER_ID}:${GROUP_ID} ${HOME}
USER ${USER_ID}

ENTRYPOINT ["entrypoint"]