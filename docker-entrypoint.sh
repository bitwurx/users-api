#!/bin/bash

if [ "$1" == "start-server" ]; then
    main
elif [ "$1" == "develop" ]; then
    cd src
    python setup.py develop
    bash
else
    exec "$@"
fi
