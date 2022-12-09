#!/usr/bin/env bash
cat $1 | jq '{"text": .abstract, "label": []}' -c
echo $1
