#!/bin/bash

mypy .
black . --check
flake8 .
isort . --check-only