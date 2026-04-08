"""
SCV: collect_market_data.py
역할: yfinance로 주요 주가지수를 수집하여 /output/raw/market_data.json 저장
실행: python .claude/scv/collect_market_data.py
"""

import json
import os
from datetime import datetime, timezone

OUTPUT_PATH = "output/raw/market_data.json"

TICKERS = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "NIKKEI": "^N225",
}


def fetch_index(name: str, ticker: str) -> dict:
    try:
        import yfinance as yf

        data = yf.Ticker(ticker)
        hist = data.history(period="2d")

        if hist.empty or len(hist) < 1:
            raise ValueError("데이터 없음")

        latest = hist.iloc[-1]
        close = round(float(latest["Close"]), 2)

        if len(hist) >= 2:
            prev_close = round(float(hist.iloc[-2]["Close"]), 2)
            change_pct = round((close - prev_close) / prev_close * 100, 2)
        else:
            change_pct = None

        return {"value": close, "change_pct": change_pct, "status": "ok"}

    except ImportError:
        return {"value": None, "change_pct": None, "status": "failed", "error": "yfinance 미설치 — pip install yfinance"}
    except Exception as e:
        return {"value": None, "change_pct": None, "status": "failed", "error": str(e)}


def main():
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    indices = {}

    for name, ticker in TICKERS.items():
        print(f"  수집 중: {name} ({ticker})")
        indices[name] = fetch_index(name, ticker)
        status = indices[name]["status"]
        value = indices[name].get("value", "N/A")
        print(f"  → {status.upper()}: {value}")

    result = {
        "collected_at": collected_at,
        "source": "yfinance",
        "indices": indices,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    ok_count = sum(1 for v in indices.values() if v["status"] == "ok")
    print(f"\n[완료] {ok_count}/{len(TICKERS)}개 지수 수집 성공 → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
