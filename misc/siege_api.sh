#!/bin/bash
siege \
    -c5 \
    -t15S \
    --content-type "application/json" \
    'https://andi.beta.gouv.fr/api/match POST < montpellier_K1706_12.json'
