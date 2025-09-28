#!/usr/bin/env bash

# The purpose of this script is to copy secrets from the developer's home
# directory to the Gitlab Runner's home directory.
# Exit on error, undefined var, pipe failure

set -euo pipefail

# Constants
readonly DEV_USER="etu"
readonly PROJECT_NAME="iac"
readonly RUNNER_HOME="/home/gitlab-runner"
readonly DEV_HOME="/home/${DEV_USER}"
readonly RUNNER_SSH_DIR="${RUNNER_HOME}/.ssh"

# Function to handle errors
error_exit() {
	echo "ERROR: $1" >&2
	exit 1
}

# Function to copy and set permissions
secure_copy() {
	local src="$1"
	local dest="$2"
	local mode="${3:-600}"

	[[ -f ${src} ]] || error_exit "Source file ${src} not found"
	cp "${src}" "${dest}" || error_exit "Failed to copy ${src} to ${dest}"
	chmod "${mode}" "${dest}"
	chown gitlab-runner:gitlab-runner "${dest}"
}

# Check if running as root
[[ ${EUID} -eq 0 ]] || error_exit "This script must be run as root"

echo "Setting up secrets for Gitlab Runner..."

# Setup Vault files
secure_copy "${DEV_HOME}/.${PROJECT_NAME}.passwd" "${RUNNER_HOME}/.${PROJECT_NAME}.passwd"
secure_copy "${DEV_HOME}/.vault.passwd" "${RUNNER_HOME}/.vault.passwd"

# Setup profile
PROFILE="${RUNNER_HOME}/.profile"
touch "${PROFILE}"
echo "export ANSIBLE_VAULT_PASSWORD_FILE=${RUNNER_HOME}/.vault.passwd" >"${PROFILE}"
chown gitlab-runner:gitlab-runner "${PROFILE}"
chmod 644 "${PROFILE}"

# Setup SSH directory
mkdir -p "${RUNNER_SSH_DIR}"
chmod 700 "${RUNNER_SSH_DIR}"
chown gitlab-runner:gitlab-runner "${RUNNER_SSH_DIR}"

# Copy SSH files
if [[ -f "${DEV_HOME}/.ssh/config" ]]; then
	secure_copy "${DEV_HOME}/.ssh/config" "${RUNNER_SSH_DIR}/config" 644
fi

# Copy all SSH keys
for key in "${DEV_HOME}"/.ssh/id_*; do
	[[ -f ${key} ]] || continue
	secure_copy "${key}" "${RUNNER_SSH_DIR}/$(basename "${key}")"
done

echo "Secrets setup completed successfully"
exit 0
