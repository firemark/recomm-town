#!/bin/bash

trap exit SIGINT
trap "kill 0" EXIT

function draw() {
  while true
  do
    python3 ./graph.py
    sleep 60
  done
}

function run() {
  python -m recomm_town $1.yaml \
    --match-time 600 \
    --output "out_$1.json" \
    --fullscreen
}

draw&
while true
do
  run mixed
  run isolated
  run community
  run shy
done
