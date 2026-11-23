#!/usr/bin/env bash
# Download the PADS dataset (PhysioNet, open access, CC BY-NC-SA 4.0) — about 1.4 GB unzipped.
# Usage: bash scripts/download_data.sh [target_dir]      (default: data/raw/pads)
set -euo pipefail
TARGET="${1:-data/raw/pads}"
mkdir -p "$TARGET"

if command -v aws >/dev/null 2>&1; then
  # Public S3 mirror; no AWS account needed. Only the 'preprocessed' folder is required for weekends 1-2.
  aws s3 sync --no-sign-request \
    s3://physionet-open/parkinsons-disease-smartwatch/1.0.0/ "$TARGET"
else
  wget -r -N -c -np -nH --cut-dirs=3 -P "$TARGET" \
    https://physionet.org/files/parkinsons-disease-smartwatch/1.0.0/
fi

echo "Done. Check that $TARGET/preprocessed/file_list.csv exists."
