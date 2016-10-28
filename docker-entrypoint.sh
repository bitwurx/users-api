#!/bin/bash

if [ "$1" == "start-server" ]; then
    main
else
    exec "$@"
fi
