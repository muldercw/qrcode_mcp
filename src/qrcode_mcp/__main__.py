"""CLI entry point for qrcode-mcp MCP server."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="qrcode-mcp",
        description="MCP server that generates awesome, stylish QR codes.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print server capabilities and available styles, then exit.",
    )
    args = parser.parse_args()

    if args.info:
        from qrcode_mcp.generator import get_capabilities
        import json

        info = {
            "name": "qrcode-mcp",
            "version": "0.1.0",
            "description": "MCP server — generate awesome QR codes with custom styles, gradients, logos, and more.",
            "capabilities": get_capabilities(),
        }
        print(json.dumps(info, indent=2))
        sys.exit(0)

    from qrcode_mcp.server import run
    run(verbose=args.verbose)


if __name__ == "__main__":
    main()
