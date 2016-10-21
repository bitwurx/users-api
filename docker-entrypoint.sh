#!/bin/bash

gunicorn users.api:api --bind 0.0.0.0:8000
