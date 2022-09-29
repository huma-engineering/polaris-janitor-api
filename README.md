# Announcement :loudspeaker: 

This repository is transferred from [gdm-SynseneHealth](https://github.com/sensynehealth/polaris-janitor-api) to Huma organisation as part of change in asset ownership 
<!-- Title - A concise title for the service that fits the pattern identified and in use across all services. -->
# Polaris Janitor API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

<!-- Description - Fewer than 500 words that describe what a service delivers, providing an informative, descriptive, and comprehensive overview of the value a service brings to the table. -->
The Janitor API is part of the Polaris platform (formerly DHOS). This service is only for non-production environments, 
and is responsible for manipulating the data in other microservices, for the purposes of development, testing, and 
maintenance of demo/training environments.

The `/dhos/v1/reset_task` HTTP endpoints can be used in combination to trigger and monitor running data resets. The POST endpoint returns HTTP 202 to indicate the task is processing, and the GET returns HTTP 200 (success), 202 (processing) or 400 (error) depending on the task status.

The `/dhos/v1/populate_gdm_task` HTTP endpoint is used to populate existing GDM patients with recent data. This will generate 
readings and messages for the specified number of days.

## Maintainers
The Polaris platform was created by Sensyne Health Ltd., and has now been made open-source. As a result, some of the
instructions, setup and configuration will no longer be relevant to third party contributors. For example, some of
the libraries used may not be publicly available, or docker images may not be accessible externally. In addition, 
CICD pipelines may no longer function.

For now, Sensyne Health Ltd. and its employees are the maintainers of this repository.

## Setup
These setup instructions assume you are using out-of-the-box installations of:
- `pre-commit` (https://pre-commit.com/)
- `pyenv` (https://github.com/pyenv/pyenv)
- `poetry` (https://python-poetry.org/)

You can run the following commands locally:
```bash
make install  # Creates a virtual environment using pyenv and installs the dependencies using poetry
make lint  # Runs linting/quality tools including black, isort and mypy
make test  # Runs unit tests
```

You can also run the service locally using the script `run_local.sh`, or in dockerized form by running:
```bash
docker build . -t <tag>
docker run <tag>
```

## Documentation
<!-- Include links to any external documentation including relevant ADR documents.
     Insert API endpoints using markdown-swagger tags (and ensure the `make openapi` target keeps them up to date).
     -->

<!-- markdown-swagger -->
 Endpoint                            | Method | Auth? | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
 ----------------------------------- | ------ | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 `/running`                          | GET    | No    | Verifies that the service is running. Used for monitoring in kubernetes.                                                                                                                                                                                                                                                                                                                                                                                                                           
 `/version`                          | GET    | No    | Get the version number, circleci build number, and git hash.                                                                                                                                                                                                                                                                                                                                                                                                                                       
 `/dhos/v1/reset_task`               | POST   | Yes   | Drops data from the microservice databases, and repopulates them with generated tests data. Passing a list of microservices in the request body will reset only those services. Responds with an HTTP 202 and a Location header - subsequent HTTP GET requests to this URL will provide the status of the task.                                                                                                                                                                                    
 `/dhos/v1/task/{task_id}`           | GET    | Yes   | Gets the result of a task by UUID. Responds with either a 202 if the task is ongoing, a 200 if it has completed, or a 400 if it has failed.                                                                                                                                                                                                                                                                                                                                                        
 `/dhos/v1/populate_gdm_task`        | POST   | Yes   | Note: despite the name, this endpoint adds data for both GDM and DBM patients. Populate GDM and DBM patients with recent data. Data consists of readings and messages. You can configure the number of recent days you want to add data for using the (optional) query parameter; 1 means generate data for yesterday, 2 means yesterday and the day before, etc. Responds with an HTTP 202 and a   Location header - subsequent HTTP GET requests to this URL will provide the status of the task.
 `/dhos/v1/clinician/jwt`            | GET    | No    | Retrieve a clinician JWT from Auth0.                                                                                                                                                                                                                                                                                                                                                                                                                                                               
 `/dhos/v1/patient/{patient_id}/jwt` | GET    | No    | Retrieve a patient JWT from Activation Auth API. Involves creation of a patient activation, and validation of that activation.                                                                                                                                                                                                                                                                                                                                                                     
 `/dhos/v1/system/{system_id}/jwt`   | GET    | No    | Retrieve a system JWT from System Auth API                                                                                                                                                                                                                                                                                                                                                                                                                                                         
<!-- /markdown-swagger -->

## Requirements
<!-- An outline of what other services, tooling, and libraries needed to make a service operate, providing a
  complete list of EVERYTHING required to work properly. -->
  At a minimum you require a system with Python 3.9. Tox 3.20 is required to run the unit tests, docker with docker-compose are required to run integration tests. See [Development environment setup](https://sensynehealth.atlassian.net/wiki/spaces/SPEN/pages/3193270/Development%2Benvironment%2Bsetup) for a more detailed list of tools that should be installed.
  
## Deployment
<!-- Setup - A step by step outline from start to finish of what is needed to setup and operate a service, providing as
  much detail as you possibly for any new user to be able to get up and running with a service. -->
  
  All development is done on a branch tagged with the relevant ticket identifier.
  Code may not be merged into develop unless it passes all CircleCI tests.
  :partly_sunny: After merging to develop tests will run again and if successful the code is built in a docker container and uploaded to our Azure container registry. It is then deployed to test environments controlled by Kubernetes.

## Testing
<!-- Testing - Providing details and instructions for mocking, monitoring, and testing a service, including any services or
  tools used, as well as links or reports that are part of active testing for a service. -->

### Unit tests
:microscope: Either use `make` or run `tox` directly.

<!-- markdown-make Makefile tox.ini -->
`tox` : Running `make test` or tox with no arguments runs `tox -e lint,default`

`make clean` : Remove tox and pyenv virtual environments.

`tox -e debug` : Runs last failed unit tests only with debugger invoked on failure. Additional py.test command line arguments may given preceded by `--`, e.g. `tox -e debug -- -k sometestname -vv`

`make default` (or `tox -e default`) : Installs all dependencies, verifies that lint tools would not change the code, runs security check programs then runs unit tests with coverage. Running `tox -e py39` does the same but without starting a database container.

`tox -e flask` : Runs flask within the tox environment. Pass arguments after `--`. e.g. `tox -e flask -- --help` for a list of commands. Use this to create database migrations.

`make help` : Show this help.

`make lint` (or `tox -e lint`) : Run `black`, `isort`, and `mypy` to clean up source files.

`make openapi` (or `tox -e openapi`) : Recreate API specification (openapi.yaml) from Flask blueprint

`make pyenv` : Create pyenv and install required packages (optional).

`make readme` (or `tox -e readme`) : Updates the README file with database diagram and commands. (Requires graphviz `dot` is installed)

`make test` : Test using `tox`

`make update` (or `tox -e update`) : Updates the `poetry.lock` file from `pyproject.toml`

<!-- /markdown-make -->

## Integration tests
:nut_and_bolt: Integration tests are located in the `integration-tests` sub-directory. After changing into this directory you can run the following commands:

<!-- markdown-make integration-tests/Makefile -->
<!-- /markdown-make -->

## Configuration
<!-- Configuration - An outline of all configuration and environmental variables that can be adjusted or customized as part
  of service operations, including as much detail on default values, or options that would produce different known
  results for a service. -->
  * `LOG_LEVEL=ERROR|WARN|INFO|DEBUG` sets the log level
  * `LOG_FORMAT=colour|plain|json` configure logging format. JSON is used for the running system but the others may be more useful during development.
