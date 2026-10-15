#!/usr/bin/env python
"""
Standalone FastMCP Weather Server
Can be run via stdio or sse for integration with Claude Desktop, Cursor, Antigravity IDE, etc.

Usage:
    python mcp_server.py                  # runs stdio transport (default)
    python mcp_server.py --transport sse  # runs SSE transport
"""
import sys
import argparse
from app.mcp_tools import mcp_server

def main():
    parser = argparse.ArgumentParser(description="Weather Intelligence MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport protocol (default: stdio)"
    )
    args = parser.parse_args()
    
    # Configure UTF-8 on Windows for stdio
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print(f"Starting Weather FastMCP Server using transport: {args.transport}...", file=sys.stderr)
    mcp_server.run(transport=args.transport)

if __name__ == "__main__":
    main()
