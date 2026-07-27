#!/usr/bin/env bash
# Minimal SageMaker GPU notebook hardware report.
# Usage: sudo ./collect_sagemaker_hardware_info.sh [output-file]

set -uo pipefail

OUTPUT_FILE="${1:-./sagemaker-hardware-info-$(date -u +%Y%m%dT%H%M%SZ).txt}"
if ! touch "$OUTPUT_FILE" 2>/dev/null; then
  echo "ERROR: Cannot write to: $OUTPUT_FILE" >&2
  exit 1
fi
exec > >(tee "$OUTPUT_FILE") 2>&1

section() {
  printf '\n===== %s =====\n' "$1"
}

run() {
  local title="$1"
  shift
  section "$title"
  if command -v "$1" >/dev/null 2>&1; then
    "$@" || printf '[command exited with status %s]\n' "$?"
  else
    printf '[command not found: %s]\n' "$1"
  fi
}

section "REPORT"
printf 'Collected (UTC): %s\n' "$(date -u --iso-8601=seconds)"
printf 'Hostname: %s\n' "$(hostname)"

section "SAGEMAKER / EC2 INSTANCE"
if command -v curl >/dev/null 2>&1; then
  IMDS_BASE='http://169.254.169.254/latest'
  IMDS_TOKEN="$(curl -fsS --connect-timeout 1 --max-time 2 -X PUT \
    -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' "$IMDS_BASE/api/token" 2>/dev/null || true)"
  if [[ -n "$IMDS_TOKEN" ]]; then
    for item in \
      'Instance type|meta-data/instance-type' \
      'Instance ID|meta-data/instance-id' \
      'Region|meta-data/placement/region' \
      'Availability zone|meta-data/placement/availability-zone' \
      'AMI ID|meta-data/ami-id'; do
      label="${item%%|*}"
      path="${item#*|}"
      value="$(curl -fsS --connect-timeout 1 --max-time 2 \
        -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" "$IMDS_BASE/$path" 2>/dev/null || true)"
      printf '%-20s %s\n' "$label:" "${value:-[unavailable]}"
    done
    printf '%-20s %s\n' 'IMDS access:' 'IMDSv2 token request succeeded'
  else
    printf 'IMDSv2 metadata unavailable or blocked.\n'
  fi
  unset IMDS_TOKEN
else
  printf '[command not found: curl]\n'
fi

section "OS / KERNEL"
if [[ -r /etc/os-release ]]; then
  # shellcheck disable=SC1091
  source /etc/os-release
  printf 'Operating system: %s\n' "${PRETTY_NAME:-unknown}"
fi
printf 'Kernel: %s\n' "$(uname -sr)"
printf 'Architecture: %s\n' "$(uname -m)"

section "CPU / MEMORY / STORAGE"
if command -v lscpu >/dev/null 2>&1; then
  lscpu | grep -E '^(Model name|CPU\(s\)|Thread\(s\) per core|Core\(s\) per socket|Socket\(s\)|NUMA node\(s\)):' || true
fi
if command -v free >/dev/null 2>&1; then
  free -h | awk 'NR == 1 || /^Mem:/ || /^Swap:/'
fi
if command -v lsblk >/dev/null 2>&1; then
  printf '\nBlock devices:\n'
  lsblk -e 7 -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL
fi
if command -v df >/dev/null 2>&1; then
  printf '\nMounted filesystem containing this report:\n'
  df -hT "$OUTPUT_FILE"
fi

run "NVIDIA-SMI" nvidia-smi
run "NVIDIA GPU LIST" nvidia-smi -L

section "CUDA COMPILER"
if command -v nvcc >/dev/null 2>&1; then
  printf 'nvcc path: %s\n' "$(command -v nvcc)"
  nvcc --version
else
  printf '[command not found: nvcc]\n'
fi

section "NVIDIA KERNEL MODULES"
if command -v lsmod >/dev/null 2>&1; then
  lsmod | grep -E '^(nvidia|nouveau)' || printf '[no NVIDIA/nouveau modules found]\n'
else
  printf '[command not found: lsmod]\n'
fi

run "DOCKER INFO" docker info

section "NVIDIA CONTAINER TOOLKIT"
if command -v nvidia-container-cli >/dev/null 2>&1; then
  printf 'nvidia-container-cli path: %s\n' "$(command -v nvidia-container-cli)"
  nvidia-container-cli --version
else
  printf '[command not found: nvidia-container-cli]\n'
fi

section "COMPLETE"
printf 'Report written to: %s\n' "$OUTPUT_FILE"
