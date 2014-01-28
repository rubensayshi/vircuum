#!/bin/bash

VERSION=$1

# $VERSION is required
[ -z "${VERSION}" ] && echo "PLEASE SPECIFY VERSION" && exit 1

BUILD="vircuum-${VERSION}"
DIR="./build/${BUILD}"

rm -rf ./build
mkdir ./build

mkdir ${DIR}
mkdir ${DIR}/tmp
cp ./run.py ${DIR}/
cp ./config.example.py ${DIR}/
cp ./README.md ${DIR}/
cp ./requirements.txt ${DIR}/
cp -r ./vircuum ${DIR}/vircuum

find ${DIR} -name "*.pyc" -exec rm -rf {} \;

cd ./build
tar cvzf ${BUILD}.tar.gz ${BUILD}

