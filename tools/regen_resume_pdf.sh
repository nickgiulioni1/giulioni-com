#!/usr/bin/env bash
#
# Regenerate assets/nick-giulioni-resume.pdf from career/index.html.
#
# - Spins up a local http.server, renders /career/ with headless Chrome in
#   print emulation, writes the PDF, and tears the server down.
# - Validates the PDF: pdfinfo page count <= 2, pdftotext must contain the
#   resume headline, the contact email, the LinkedIn URL, and "Ballpark".
#
# Re-running this script overwrites the existing PDF. It is safe to re-run;
# the server is killed on EXIT/INT/TERM and the temp file is removed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_PDF="${REPO_ROOT}/assets/nick-giulioni-resume.pdf"
SOURCE_URL_PATH="/career/"
PORT="${RESUME_PDF_PORT:-${PORT:-0}}"
SERVER_LOG="$(mktemp -t resume_pdf_server.XXXXXX.log)"
SERVER_PID=""

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
  exit "${exit_code}"
}
trap cleanup EXIT INT TERM

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

if ! grep -q '^assets/$' "${REPO_ROOT}/.gitignore" 2>/dev/null && [[ ! -f "${OUTPUT_PDF}" ]]; then
  :
fi

# Start the local server. Use python3 http.server so we don't introduce
# other build dependencies. Background it, redirect output to a temp log.
(
  cd "${REPO_ROOT}"
  python3 -m http.server "${PORT}" --bind 127.0.0.1 >"${SERVER_LOG}" 2>&1 &
  echo $! >"${SERVER_LOG}.pid"
) </dev/null

# Wait for the server to accept connections (max ~10s).
for _ in $(seq 1 50); do
  if curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" 2>/dev/null; then
    break
  fi
  sleep 0.2
done

if [[ ! -s "${SERVER_LOG}.pid" ]]; then
  echo "Failed to start local http.server; see ${SERVER_LOG}" >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 3
fi
SERVER_PID="$(cat "${SERVER_LOG}.pid")"
rm -f "${SERVER_LOG}.pid"

if ! curl -fsS -o /dev/null "http://127.0.0.1:${PORT}${SOURCE_URL_PATH}"; then
  echo "Local server did not respond at ${SOURCE_URL_PATH}." >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 3
fi

mkdir -p "$(dirname "${OUTPUT_PDF}")"
TMP_PDF="$(mktemp -t nick-giulioni-resume.XXXXXX.pdf)"
trap 'rm -f "${TMP_PDF}"; cleanup' EXIT INT TERM

# Generate the PDF with print emulation. The CSS @page rule (Letter size)
# and the @media print block render the recruiter-ready resume.
"${CHROME_BIN}" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --hide-scrollbars \
  --no-pdf-header-footer \
  --print-to-pdf="${TMP_PDF}" \
  --virtual-time-budget=15000 \
  "http://127.0.0.1:${PORT}${SOURCE_URL_PATH}" \
  >/dev/null

if [[ ! -s "${TMP_PDF}" ]]; then
  echo "Chrome produced no PDF; check ${SERVER_LOG}." >&2
  cat "${SERVER_LOG}" >&2 || true
  exit 4
fi

# pdfinfo page count check.
PAGE_COUNT="$("${PDFINFO_BIN}" "${TMP_PDF}" | awk '/^Pages:/{print $2}')"
if [[ -z "${PAGE_COUNT}" || "${PAGE_COUNT}" -gt 2 ]]; then
  echo "PDF page count must be <= 2 (got ${PAGE_COUNT:-unknown})." >&2
  exit 5
fi

# pdftotext content check.
TEXT="$("${PDFTOTEXT_BIN}" -layout "${TMP_PDF}" -)"
# The page kicker carries letter-spaced uppercase RESUME; match it
# case-insensitively so the validator survives typographic transforms.
TEXT_LOWER="$(tr '[:upper:]' '[:lower:]' <<<"${TEXT}")"
for needle in "resume" "nick@giulioni.com" "linkedin.com/in/nickgiulioni" "ballpark"; do
  if ! grep -qF -- "${needle}" <<<"${TEXT_LOWER}"; then
    echo "PDF text missing required token: ${needle}" >&2
    exit 6
  fi
done

mv "${TMP_PDF}" "${OUTPUT_PDF}"
trap cleanup EXIT INT TERM

echo "Wrote ${OUTPUT_PDF} (${PAGE_COUNT} page(s))."
