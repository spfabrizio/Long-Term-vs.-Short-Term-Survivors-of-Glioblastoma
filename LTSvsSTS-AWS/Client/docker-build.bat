@echo off
REM
REM Windows BATCH script to build docker container
REM
@echo on
docker rmi ltsvssts-client-aws-main
docker build -t ltsvssts-client-aws-main .
