#!/bin/bash
workers=(1 2 5 10 20 30 50 80 130 210 340)
for i in "${workers[@]}"
do
    echo "====>> Testing siege with $i workers"
    siege \
        -c$i \
        -t15S \
        --content-type "application/json" \
        'https://andi.beta.gouv.fr/api/match POST < montpellier_K1706_12.json'
    echo ""
done
