#!/bin/bash
# Total path override
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
# Use absolute path to npx directly
exec /opt/homebrew/bin/npx -y @modelcontextprotocol/server-filesystem "$@"
