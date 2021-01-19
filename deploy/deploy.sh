#!/bin/bash

set -euxo pipefail


VAULT_PASSWORD_FILE=${VAULT_PASSWORD_FILE:-vaults/dev/secret-vars.yml}

# if the file does not exist
if ! [[ -f $VAULT_PASSWORD_FILE ]]; then
	echo "please have the file '$VAULT_PASSWORD_FILE' for this"
	echo "script to work correctly"
	exit 1
fi

options=

# if no argument was given
if [[ $# -eq 0 ]] ; then
	# run command as a local user
	options='--ask-vault-pass'
fi

ansible-playbook config.yml \
	-e "@${VAULT_PASSWORD_FILE}" \
	${options}


