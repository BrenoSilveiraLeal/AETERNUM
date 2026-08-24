"""Safe local MetaTrader 5 diagnostic.

Run from the backend directory with:
    python -m app.tools.mt5_doctor
"""

import json
import sys

from ..broker.registry import get_mt5_broker


def main() -> int:
    broker = get_mt5_broker()
    status = broker.status()
    output = {
        "package_available": broker.mt5 is not None,
        "connected": status["connected"],
        "terminal": status["terminal"],
        "market_data": status["market_data"],
        "environment": status["environment"],
        "account": status["account"],
        "message": status["message"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if status["connected"] and (status["account"] or {}).get("permitted_demo") else 1


if __name__ == "__main__":
    sys.exit(main())
