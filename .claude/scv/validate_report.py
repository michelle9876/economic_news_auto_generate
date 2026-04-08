"""
SCV: validate_report.py
역할: 리포트 품질 검증 (필수 수치, 뉴스 수, 인사이트 길이)
실행: python .claude/scv/validate_report.py --date 20260408 --type morning
출력: /output/logs/validation_YYYYMMDD_[morning|closing].json
"""

import argparse
import json
import os
from datetime import datetime, timezone


def load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_load_error": str(e)}


def load_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def check_required_data(market: dict, macro: dict) -> dict:
    """주가지수 1개 이상 + 금리 또는 환율 1개 이상"""
    indices = market.get("indices", {})
    indicators = macro.get("indicators", {})

    ok_indices = [k for k, v in indices.items() if v.get("status") == "ok"]
    ok_rates = [
        k
        for k in ["usd_krw", "us_10y_yield", "fed_funds_rate"]
        if indicators.get(k, {}).get("status") == "ok"
    ]

    passed = len(ok_indices) >= 1 and len(ok_rates) >= 1
    return {
        "pass": passed,
        "detail": f"주가지수 ok: {ok_indices}, 금리/환율 ok: {ok_rates}",
    }


def check_news_count(news: dict) -> dict:
    """뉴스 3개 이상"""
    count = news.get("count", 0)
    return {
        "pass": count >= 3,
        "count": count,
        "required": 3,
    }


def check_insight_length(insight_text: str) -> dict:
    """인사이트 본문 200자 이상"""
    length = len(insight_text.strip())
    return {
        "pass": length >= 200,
        "length": length,
        "required": 200,
    }


def determine_overall(results: dict) -> str:
    """전체 검증 결과: pass / warn / fail"""
    flags = [k for k, v in results.items() if not v.get("pass", True)]
    if not flags:
        return "pass"
    # 필수 데이터가 없으면 warn (발행은 하되 경고)
    return "warn"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="날짜 (YYYYMMDD)")
    parser.add_argument(
        "--type", required=True, choices=["morning", "closing"], help="리포트 타입"
    )
    args = parser.parse_args()

    date_str = args.date
    report_type = args.type

    # 파일 경로
    market_path = "output/raw/market_data.json"
    macro_path = "output/raw/macro_data.json"
    news_path = "output/raw/news_data.json"
    insight_path = "output/drafts/insight_draft.md"
    output_path = f"output/logs/validation_{date_str}_{report_type}.json"

    print(f"[검증 시작] {date_str} {report_type}")

    # 데이터 로드
    market = load_json(market_path)
    macro = load_json(macro_path)
    news = load_json(news_path)
    insight_text = load_text(insight_path)

    # 검증 실행
    results = {
        "required_data": check_required_data(market, macro),
        "news_count": check_news_count(news),
        "insight_length": check_insight_length(insight_text),
    }

    # 실패 플래그 수집
    flags = [k for k, v in results.items() if not v.get("pass", True)]

    overall = determine_overall(results)

    output = {
        "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "date": date_str,
        "report_type": report_type,
        "results": results,
        "overall": overall,
        "flags": flags,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 결과 출력
    print(f"\n[검증 결과] overall: {overall.upper()}")
    for key, val in results.items():
        status = "PASS" if val.get("pass") else "WARN"
        detail = val.get("detail") or val.get("count") or val.get("length") or ""
        print(f"  {status}  {key}: {detail}")

    if flags:
        print(f"\n  경고 항목: {flags}")
        print("  → N/A 표시 후 리포트 발행을 계속 진행합니다.")

    print(f"\n[완료] → {output_path}")


if __name__ == "__main__":
    main()
