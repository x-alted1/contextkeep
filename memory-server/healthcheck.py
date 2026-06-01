"""Container healthcheck: MCP HTTP endpoint is listening."""

import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    port = os.environ.get("MCP_PORT", "8080")
    url = f"http://127.0.0.1:{port}/mcp"
    try:
        urllib.request.urlopen(url, timeout=3)
    except urllib.error.HTTPError:
        # Bare GET often returns 4xx; that still means the server is up.
        pass
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
