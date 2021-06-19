# RSS Reader API

## Readme Notes

* If the command line starts with $, the command should run with user privileges
* If the command line starts with #, the command should run with root privileges


## Retrieve code

* `$ git clone https://github.com/DicksonChi/rss-reader-api.git`


## Installation

* Install [docker](https://docs.docker.com/engine/install/) and
* Install [docker-compose](https://docs.docker.com/compose/install/)
* Make sure you can [run docker as non-sudo](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)


## Running

* `$ docker-compose up`


## API Specification
After you run, go to this link

http://127.0.0.1:8000/api/v1/docs/

## Testing

* `$ docker exec -it rss_reader_web_1 poetry run pytest tests/python `


### To run black
* `$ docker exec -it rss_reader_web_1 poetry run black --skip-string-normalization --line-length=120 src`
* `$ docker exec -it rss_reader_web_1 poetry run black --skip-string-normalization --line-length=120 tests`


### To run mypy we need to run it inside the src folder
* `$ docker exec -it rss_reader_web_1 poetry run bash`
* `$ cd src/ `
* `$ mypy .`


## Notes:

* In the development environment, you can login in the admin console using `admin/admin`.
* If you run into any issues with permissions while editing a file, run `sudo chown -R $(whoami) .` (because when files
  are generated inside the docker container, they are owned by root).
* Notice that when running commands in the backend container, we are prepending `poetry run` to the command passed. This
  is so that we go inside the "poetry environment", where the python packages are installed.