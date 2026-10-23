#!/usr/bin/env bash
#
# Regenerate assets/nick-giulioni-resume.pdf from career/index.html.
#
# - Spins up a local http.server, renders /career/ with headless Chrome in
#   print emulation, writes the PDF, and tears the server down.
# - Validates the PDF: pdfinfo page count <= 2, pdftotext must contain the
#   resume headline, the contact email, the LinkedIn URL, and "Ballpark".
#
# Set OUT to write elsewhere. The destination is replaced only after validation.
# The server and temporary files are cleaned up on EXIT/INT/TERM.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_PDF="${OUT:-${REPO_ROOT}/assets/nick-giulioni-resume.pdf}"
SOURCE_URL_PATH="/career/"
PORT="${RESUME_PDF_PORT:-${PORT:-0}}"
SERVER_LOG="$(mktemp -t resume_pdf_server.XXXXXX.log)"
SERVER_PID=""
TMP_PDF=""
START_MARKER=""

CHROME_BIN="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PDFINFO_BIN="${PDFINFO_BIN:-pdfinfo}"
PDFTOTEXT_BIN="${PDFTOTEXT_BIN:-pdftotext}"

cleanup() {
  local exit_code=$?
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
  if [[ -f "${SERVER_LOG}" ]]; then
    rm -f "${SERVER_LOG}"
  fi
  rm -f "${TMP_PDF}" "${START_MARKER}" || true
  exit "${exit_code}"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ ! -x "${CHROME_BIN}" ]]; then
  echo "Chrome not found at ${CHROME_BIN}; set CHROME_BIN to override." >&2
  exit 2
fi
if ! command -v "${PDFINFO_BIN}" >/dev/null 2>&1; then
  echo "pdfinfo not on PATH; set PDFINFO_BIN to override." >&2
  exit 2
fi
if ! command -v "${PDFTOTEXT_BIN}" >/dev/null 2>&1; then
  echo "pdftotext not on PATH; set PDFTOTEXT_BIN to override." >&2
  exit 2
fi

if [[ "${PORT}" == "0" ]]; then
  PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')"
fi

# Start the local server. Use python3 http.server so we don't introduce
# other build dependencies. Background it, redirect output to a temp log.
(
  cd "${REPO_ROOT}"
  exec python3 -m http.server "${PORT}" --bind 127.0.0.1
) </dev/null >"${SERVER_LOG}" 2>&1 &
SERVER_PID=$!

# Wait for the server to accept connections (max ~10s).
for _ in $(seq 1 50); do
  if curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" 2>/dev/null; then
    break
  fi
  sleep 0.2
done

if ! curl -fsS -o /dev/null "http://127.0.0.1:${PORT}${SOURCE_URL_PATH}"; then
  echo "Local server did not respond at ${SOURCE_URL_PATH}." >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 3
fi

mkdir -p "$(dirname "${OUTPUT_PDF}")"
TMP_PDF="$(mktemp "${OUTPUT_PDF}.tmp.XXXXXX")"
START_MARKER="$(mktemp "${OUTPUT_PDF}.start.XXXXXX")"

# Generate the PDF with print emulation. The CSS @page rule (Letter size)
# and the @media print block render the recruiter-ready resume.
CHROME_STATUS=0
"${CHROME_BIN}" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --hide-scrollbars \
  --no-pdf-header-footer \
  --print-to-pdf="${TMP_PDF}" \
  --virtual-time-budget=15000 \
  "http://127.0.0.1:${PORT}${SOURCE_URL_PATH}" \
  >/dev/null || CHROME_STATUS=$?

# macOS Bash 3.2 compares -nt timestamps at whole-second precision.
if [[ ! -s "${TMP_PDF}" ]] || ! python3 - "${TMP_PDF}" "${START_MARKER}" <<'PYTHON'
import os
import sys
sys.exit(0 if os.stat(sys.argv[1]).st_mtime_ns > os.stat(sys.argv[2]).st_mtime_ns else 1)
PYTHON
then
  echo "Chrome exited ${CHROME_STATUS} and produced no fresh, non-empty PDF; destination unchanged." >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 4
fi

# pdfinfo page count check.
if ! PAGE_COUNT="$("${PDFINFO_BIN}" "${TMP_PDF}" | awk '/^Pages:/{print $2}')"; then
  echo "pdfinfo could not read the generated PDF; destination unchanged." >&2
  exit 5
fi
if [[ ! "${PAGE_COUNT}" =~ ^[12]$ ]]; then
  echo "PDF page count must be 1 or 2 (got ${PAGE_COUNT:-unknown}); destination unchanged." >&2
  exit 5
fi

# pdftotext content check.
if ! TEXT="$("${PDFTOTEXT_BIN}" -layout "${TMP_PDF}" -)"; then
  echo "pdftotext could not read the generated PDF; destination unchanged." >&2
  exit 6
fi
# The page kicker carries letter-spaced uppercase RESUME; match it
# case-insensitively so the validator survives typographic transforms.
TEXT_LOWER="$(tr '[:upper:]' '[:lower:]' <<<"${TEXT}")"
for needle in "resume" "nick@giulioni.com" "linkedin.com/in/nickgiulioni" "ballpark"; do
  if ! grep -qF -- "${needle}" <<<"${TEXT_LOWER}"; then
    echo "PDF text missing required token: ${needle}" >&2
    exit 6
  fi
done

if [[ "${CHROME_STATUS}" -ne 0 ]]; then
  echo "Chrome exited ${CHROME_STATUS}, but the fresh PDF passed all checks; accepting it." >&2
fi

mv -f "${TMP_PDF}" "${OUTPUT_PDF}"

echo "Wrote ${OUTPUT_PDF} (${PAGE_COUNT} page(s))."
