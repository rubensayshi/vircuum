#!/bin/bash

ENV=$1

# $ENV is required
[ -z "${ENV}" ] && echo "PLEASE SPECIFY ENV" && exit 1
# dev = development
[ "${ENV}" == "dev" ] && ENV="development"
# ensure ENVIRONMENT is set, default to development
[ -z "${ENVIRONMENT}" ] && ENVIRONMENT="development" && export ENVIRONMENT

# specified ENV has to be same as ENVIRONMENT
[ "${ENVIRONMENT}" != "${ENV}" ] && echo "\$ENVIRONMENT[${ENVIRONMENT}] != \$ENV[${ENV}]" && exit 1

echo ">> ENV [${ENV}]"

# ensure we're in the root of the project
[ `basename $(pwd)` != "vircu" ] && echo "your current pwd should be 'vircu'" && exit 1

# determine rootdir
[ -z "$ROOT" ] && ROOT=`php -r "echo dirname(dirname(realpath('$(pwd)/$0')));"` && export ROOT

LOGDIR="${ROOT}/tmp/logs"
PIDDIR="${ROOT}/tmp/run"
ENVDIR="${ROOT}/env"
CNFDIR="${ROOT}/cnf"

sudo mkdir -p $LOGDIR
sudo mkdir -p $PIDDIR
sudo chmod -R 0777 $LOGDIR
sudo chmod -R 0777 $PIDDIR

if [[ "${ENV}" == "development" ]]; then
    ENV=""
    ENVEXT=""
else
    ENVEXT=".${ENV}"
fi

echo ">> activate env"
source ${ENVDIR}/bin/activate

echo ">> git pull"
git pull

echo ">> pip install"
pip install -r requirements.txt

echo ">> grunt"
grunt

echo ">> build versions"
${ENVDIR}/bin/python ${ROOT}/tasks.py build versions

echo ">> uwsgi reload"
sudo /etc/init.d/uwsgi reload

echo ">> supervisor -HUP"
SUPERVISOR=`ps -ef | grep "${CNFDIR}/supervisor${ENVEXT}.ini" | grep -v "grep"`

if [ -z "${SUPERVISOR}" ]; then
    echo "starting new supervisor"
    ${ENVDIR}/bin/python ${ENVDIR}/bin/supervisord -c ${CNFDIR}/supervisor${ENVEXT}.ini
else
    echo "restarting supervisor"
    ps -ef | grep "${CNFDIR}/supervisor${ENVEXT}.ini" | grep -v "grep" | awk '{print $2}' | xargs kill -s HUP
fi
