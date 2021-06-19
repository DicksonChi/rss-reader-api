FROM python:3.9.5
LABEL maintainer="Dickson Chibuzor <dickson.ek.chibuzor@gmail.com>"

ENV PYTHONUNBUFFERED 1
ARG POETRY_INSTALL_OPTIONS="--no-dev"
ARG USER_ID="1000"
ARG GROUP_ID="1000"

# Create a non root user so that we don't run the container as root
RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

ENV PATH="/home/user/.local/bin:${PATH}"

COPY . /django
WORKDIR /django

COPY ./docker/develop/entrypoint.sh /entrypoint.sh
COPY ./docker/develop/worker-entrypoint.sh /worker-entrypoint.sh
COPY ./docker/develop/scheduler-entrypoint.sh /scheduler-entrypoint.sh
# RUN chmod +x /entrypoint.sh
# ENTRYPOINT ["/entrypoint.sh"]

RUN pip install poetry && poetry config experimental.new-installer false && poetry install $POETRY_INSTALL_OPTIONS
