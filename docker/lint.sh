#!/bin/bash

mypy .
black .
flake8 .
isort .