#!/bin/bash
SCRIPT_DIR=$(realpath $( dirname "${BASH_SOURCE[0]}" ) )

type=$1
auth_types=( dev deploy repo)

target="pyproject.toml"


function activate() {
    src="${type}.${target}"
    cp "${SCRIPT_DIR}/${src}" "${SCRIPT_DIR}/$target"
}


if [[ " ${auth_types[@]} " =~ " ${type} " ]]; then
    activate $type
    echo "$type activated on ${SCRIPT_DIR}"
else
    echo "Please provide a configuration among:"
    for i in "${auth_types[@]}"
    do
        echo  " - $i"
    done
fi
