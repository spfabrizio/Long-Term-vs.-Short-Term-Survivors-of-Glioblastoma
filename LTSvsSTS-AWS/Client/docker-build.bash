#!/bin/bash
#
# Linux/Mac BASH script to build docker container
#
docker rmi ltsvssts-client-aws-main
docker build -t ltsvssts-client-aws-main .
