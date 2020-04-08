# BASH COMPATIBLE
# Only export if not already defined

# Postgresql DSN
export PG_DSN="${PG_DSN:=postgres://user:password@localhost/database}"

# Service log level
export LOG_LEVEL="${LOG_LEVEL:=info}"

# Server host address, port and proxy prefix
export HOST="${HOST:=localhost}"
export PORT="${PORT:=5000}"
export PROXY_PREFIX="${PROXY_PREFIX:='/'}"

# Force re-build rome suggestion data file
export FORCE_BUILD="${FORCE_BUILD:=false}"

# Disable asyncpg, for CI testing only
export NO_ASYNCPG="${NO_ASYNCPG:=false}"
