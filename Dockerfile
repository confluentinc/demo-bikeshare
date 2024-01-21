FROM python:3

## confluent CLI uses this as a value for authentication - user can provide another if they'd prefer, but if it's
## not static from container instance to container instance it prevents confluent CLI auth from being cached
## python will batch logs, and this can lead to things looking like they're not working
ENV PYTHONUNBUFFERED=1
ENV MACHINE_ID=64a4eec8-f63f-422c-873b-faff6a3cb3f3
RUN echo ${MACHINE_ID} > /etc/machine-id

## global dependencies
RUN apt update
RUN apt install -y tmux gnupg software-properties-common jq gettext-base

## terraform install
## https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" |  tee /etc/apt/sources.list.d/hashicorp.list
RUN apt update
RUN apt-get install -y terraform

## poetry install
## https://python-poetry.org/docs/#installation
RUN curl -sSL https://install.python-poetry.org |  POETRY_HOME=/usr/local python3 -

## confluent cli install
## https://docs.confluent.io/confluent-cli/current/install.html#cli-install
RUN curl -L --http1.1 https://cnfl.io/cli | sh -s -- -b /usr/local/bin

## install app dependencies
ENV INSTALL_DIR=/opt/bikeshare
WORKDIR ${INSTALL_DIR}
COPY pyproject.toml .
RUN poetry install 

## development workaround - make sure we don't override poetry.lock inside the container with one we're copying from local
RUN mv poetry.lock poetry.lock.bak
## move everything else into container
COPY . .
## move the original poetry.lock back
RUN mv poetry.lock.bak poetry.lock

## install the app into the environment - as it wasn't there when we did this before
RUN poetry install 

## initialize terraform
WORKDIR ${INSTALL_DIR}/terraform
RUN terraform init
