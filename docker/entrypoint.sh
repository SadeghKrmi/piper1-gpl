#!/usr/bin/env bash
VALID_COMMANDS=("speak" "download" "server" "server-dev")

DATA_DIR='/data'
COMMAND="$1"
shift

case "${COMMAND}" in
  speak)
    exec python3 -m piper --data-dir "${DATA_DIR}" "$@"
    ;;
  download)
    exec python3 -m piper.download_voices --data-dir "${DATA_DIR}" "$@"
    ;;
  server)
    # Production server with Gunicorn
    echo "Starting production server with Gunicorn..."
    export PYTHONPATH=/app:/app/src:$PYTHONPATH
    cd /app
    exec gunicorn \
      --bind 0.0.0.0:5000 \
      --workers ${GUNICORN_WORKERS:-2} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --log-level ${LOG_LEVEL:-info} \
      --access-logfile - \
      --error-logfile - \
      piper.wsgi:application
    ;;
  server-dev)
    # Development server (original Flask)
    exec python3 -m piper.http_server --host 0.0.0.0 --data-dir "${DATA_DIR}" "$@"
    ;;
  ""|help|-h|--help)
    echo "Usage: <command> [args...]"
    echo "Available commands:"
    echo "  speak        Synthesize audio from text"
    echo "  download     Download voices"
    echo "  server       Run production server with Gunicorn"
    echo "  server-dev   Run development server with Flask"
    exit 0
    ;;
  *)
    echo "Error: Unknown command '$COMMAND'"
    echo "Run with --help for usage."
    exit 1
    ;;
esac