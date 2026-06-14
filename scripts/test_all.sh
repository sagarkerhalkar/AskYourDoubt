#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN="$ROOT/test_results/qa_runs/$STAMP"
mkdir -p "$RUN/temp" "$RUN/device_results"

export TMPDIR="$RUN/temp"
export TEMP="$RUN/temp"
export TMP="$RUN/temp"
export AYD_DEVICE_RESULTS_ROOT="$RUN/device_results"

python -m pip install --dry-run -r requirements-dev.txt
python -m compileall -q app.py db.py auth.py utils.py routes
python -c "import app; rules=list(app.app.url_map.iter_rules()); print('Registered routes:',len(rules)); assert len(rules)>=45"
python -m pytest -q tests \
  --basetemp "$RUN/pytest_core" \
  -p no:cacheprovider \
  --junitxml "$RUN/core-junit.xml"

python run_device_matrix.py

if [[ "${FULL_BROWSER_MATRIX:-0}" == "1" ]]; then
  python -m playwright install chromium firefox webkit
  python -m pytest -q browser_tests \
    --browser chromium \
    --browser firefox \
    --browser webkit \
    --basetemp "$RUN/pytest_browser" \
    -p no:cacheprovider \
    --junitxml "$RUN/browser-junit.xml"
fi

echo "QA PASSED. Evidence: $RUN"
