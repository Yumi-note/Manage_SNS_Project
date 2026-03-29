#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install -r requirements.txt
python -m global_trend_jp_publisher.cli run-daily
