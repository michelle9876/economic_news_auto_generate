"""
SCV: collect_macro_data.py
역할: FRED API로 거시경제 지표(금리·환율·물가)를 수집하여 /output/raw/macro_data.json 저장
실행: python .claude/scv/collect_macro_data.py
환경변수: FRED_API_KEY
"""

import json
import os
from datetime import datetime, timezone

OUTPUT_PATH = "output/raw/macro_data.json"

# FRED 시리즈 ID 목록
FRED_SERIES = {
    "us_10y_yield": {
        "series_id": "DGS10",
        "label": "미국 10년물 국채 금리",
        "unit": "%",
    },
    "fed_funds_rate": {
        "series_id": "FEDFUNDS",
        "label": "미국 연방기금금리",
        "unit": "%",
    },
    "usd_krw": {
        "series_id": "DEXKOUS",
        "label": "원/달러 환율",
        "unit": "KRW",
    },
    "us_cpi_yoy": {
        "series_id": "CPIAUCSL",
        "label": "미국 CPI (전년 대비)",
        "unit": "%",
    },
}


def fetch_fred_series(series_id: str, api_key: str) -> dict:
    try:
        import urllib.request

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}"
            f"&api_key={api_key}"
            f"&file_type=json"
            f"&sort_order=desc"
            f"&limit=5"
        )

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        observations = data.get("observations", [])
        # 최근 유효값(. 아닌) 찾기
        for obs in observations:
            if obs["value"] != ".":
                return {
                    "value": round(float(obs["value"]), 4),
                    "date": obs["date"],
                    "status": "ok",
                }

        return {"value": None, "date": None, "status": "failed", "error": "유효한 관측값 없음"}

    except Exception as e:
        return {"value": None, "date": None, "status": "failed", "error": str(e)}


def main():
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        print("[경고] FRED_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  설정 방법: export FRED_API_KEY=your_key_here")

    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    indicators = {}

    for key, meta in FRED_SERIES.items():
        print(f"  수집 중: {meta['label']} ({meta['series_id']})")

        if not api_key:
            indicators[key] = {
                "value": None,
                "unit": meta["unit"],
                "label": meta["label"],
                "status": "failed",
                "error": "API 키 없음",
            }
            print(f"  → FAILED: API 키 없음")
            continue

        result = fetch_fred_series(meta["series_id"], api_key)
        indicators[key] = {
            **result,
            "unit": meta["unit"],
            "label": meta["label"],
        }
        status = result["status"]
        value = result.get("value", "N/A")
        date = result.get("date", "")
        print(f"  → {status.upper()}: {value} {meta['unit']} ({date})")

    output = {
        "collected_at": collected_at,
        "source": "FRED API",
        "indicators": indicators,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    ok_count = sum(1 for v in indicators.values() if v["status"] == "ok")
    print(f"\n[완료] {ok_count}/{len(FRED_SERIES)}개 지표 수집 성공 → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
