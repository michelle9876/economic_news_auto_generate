"""
SCV: collect_news.py
역할: NewsAPI top-headlines로 경제 뉴스를 수집하여 /output/raw/news_data.json 저장
실행: python .claude/scv/collect_news.py
환경변수: NEWS_API_KEY
참고: 무료 플랜은 /v2/everything의 날짜 필터가 제한됨 → top-headlines 사용
"""

import json
import os
from datetime import datetime, timezone

OUTPUT_PATH = "output/raw/news_data.json"

MAX_ARTICLES = 10


def fetch_news(api_key: str) -> list:
    import urllib.request
    import urllib.parse

    # top-headlines: business 카테고리 (무료 플랜 지원)
    params = urllib.parse.urlencode(
        {
            "category": "business",
            "language": "en",
            "pageSize": MAX_ARTICLES,
            "apiKey": api_key,
        }
    )

    url = f"https://newsapi.org/v2/top-headlines?{params}"

    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode())

    articles = data.get("articles", [])
    result = []
    for article in articles:
        result.append(
            {
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_at": article.get("publishedAt", ""),
                "url": article.get("url", ""),
                "description": (article.get("description") or "")[:200],
            }
        )

    return result


def main():
    api_key = os.environ.get("NEWS_API_KEY", "")
    if not api_key:
        print("[경고] NEWS_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  설정 방법: export NEWS_API_KEY=your_key_here")

    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    articles = []
    error_msg = None

    if api_key:
        try:
            print(f"  뉴스 수집 중 (business top-headlines, 최대 {MAX_ARTICLES}개)...")
            articles = fetch_news(api_key)
            print(f"  → {len(articles)}개 수집 완료")
        except Exception as e:
            error_msg = str(e)
            print(f"  → FAILED: {e}")
    else:
        error_msg = "API 키 없음"

    output = {
        "collected_at": collected_at,
        "source": "NewsAPI",
        "count": len(articles),
        "articles": articles,
    }

    if error_msg:
        output["error"] = error_msg

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    status = "성공" if len(articles) >= 3 else f"경고 (3개 미만: {len(articles)}개)"
    print(f"\n[완료] 뉴스 수집 {status} → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
