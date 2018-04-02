#!/bin/sh

kubectl patch serviceaccount default -p "{\"imagePullSecrets\": [{\"name\": \"docker-secret\"}]}"
