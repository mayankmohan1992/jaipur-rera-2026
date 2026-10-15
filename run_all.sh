#!/bin/bash
set -e
cd "$(dirname "$0")"
for s in 01_fetch_register 02_harvest_status 03_fetch_pincodes 04_pincode_names 05_build_pack 06_pincode_pack; do
  echo "=== $s ==="
  python3 scripts/$s.py || { echo "FAILED $s"; exit 1; }
done
echo "=== ALL STEPS DONE ==="
