#!/bin/bash

# Copyright 2019 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o nounset
set -o pipefail

echo PROMETHEUS_NETWORK: "${PROMETHEUS_NETWORK:-}"
echo @: $@
echo printenv
printenv
echo

# Add firewall rule for Prometheus port (9090)
if [[ -n "${PROMETHEUS_NETWORK:-}" ]]; then
  gcloud compute networks list
  gcloud compute firewall-rules list
  PROMETHEUS_RULE_NAME="${PROMETHEUS_NETWORK}-9090"
  if ! gcloud compute firewall-rules describe "${PROMETHEUS_RULE_NAME}" > /dev/null; then
    echo "Prometheus firewall rule not found, creating..."
    gcloud compute firewall-rules create --network "${PROMETHEUS_NETWORK}" --source-ranges 0.0.0.0/0 --allow tcp:9090 "${PROMETHEUS_RULE_NAME}"
    PROMETHEUS_RULE_NAME_CREATED="${PROMETHEUS_RULE_NAME}"
  fi
fi

# Try
set +o errexit
(
  set -o errexit
  echo COMMAND: ./run-e2e.sh ${@:2}
  ./run-e2e.sh ${@:2}
)

#Catch
ERR_CODE=$?
set -o errexit

if [[ -n "${PROMETHEUS_RULE_NAME_CREATED:-}" ]]; then
  echo "Deleting Prometheus firewall rule..."
  gcloud compute firewall-rules delete "${PROMETHEUS_RULE_NAME_CREATED}"
fi

exit $ERR_CODE
