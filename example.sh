#!/bin/bash

export HTTPPATH="http://localhost:8080;$HTTPPATH"

./client.py "http://localhost:8080/randomwords.txt | sort | head"