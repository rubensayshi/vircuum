#!/bin/bash

VERSION=$1

# $VERSION is required
[ -z "${VERSION}" ] && echo "PLEASE SPECIFY VERSION" && exit 1

BUILDDIR="./tmp/build"
BUILD="vircuum-${VERSION}"
DIR="${BUILDDIR}/${BUILD}"

rm -rf ${BUILDDIR}
mkdir ${BUILDDIR}

mkdir ${DIR}
mkdir ${DIR}/tmp
cp ./run.py ${DIR}/
cp ./config.example.py ${DIR}/config.py
cp ./README.md ${DIR}/
cp ./requirements.txt ${DIR}/
cp -r ./vircuum ${DIR}/vircuum

find ${DIR} -name "*.pyc" -exec rm -rf {} \;

cd ${BUILDDIR}
tar cvzf ${BUILD}.tar.gz ${BUILD}

