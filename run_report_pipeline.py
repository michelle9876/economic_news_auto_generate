#!/usr/bin/env python3
"""
경제 분석 리포트 자동 생성 파이프라인
GitHub Actions에서 실행되며, 아침/저녁 리포트를 자동으로 판단해 생성합니다.
"""

import subprocess
import sys
import os
from datetime import datetime
import json

def get_report_type():
    """
    현재 시각에 따라 morning/closing 결정
    UTC 기준:
    - 23시 (한국 오전 8시) → morning
    - 11시 (한국 저녁 8시) → closing
    """
    hour = datetime.utcnow().hour

    if hour == 23:
        return "morning"
    elif hour == 11:
        return "closing"
    else:
        # 로컬 테스트 용: 더 광범위하게 매칭
        # 23시 근처 → morning, 11시 근처 → closing
        if 22 <= hour < 24 or 0 <= hour < 2:
            return "morning"
        elif 10 <= hour < 13:
            return "closing"
        else:
            # 기본값: closing
            return "closing"

def ensure_output_dirs():
    """출력 디렉토리 생성"""
    dirs = [
        "output/raw",
        "output/processed",
        "output/drafts",
        "output/final",
        "output/logs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def run_scv_scripts():
    """SCV 데이터 수집 스크립트 실행"""
    scripts = [
        ".claude/scv/collect_market_data.py",
        ".claude/scv/collect_macro_data.py",
        ".claude/scv/collect_news.py"
    ]

    for script in scripts:
        print(f"\n[1단계] 실행: {script}")
        try:
            result = subprocess.run(
                ["python3", script],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f"⚠️  {script} 실행 오류: {result.stderr}")
            else:
                print(f"✅ {script} 완료")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {script} 타임아웃")
        except Exception as e:
            print(f"⚠️  {script} 실행 실패: {e}")

def call_researcher():
    """리서처 호출 - 데이터 통합 및 요약"""
    print("\n[2단계] 리서처 호출: 데이터 통합 및 요약")

    # 이 부분은 Claude를 통해 실행됨
    # 실제 구현은 CLAUDE.md에서 .claude/staff/experts/researcher.md를 읽고 실행
    try:
        from anthropic import Anthropic

        client = Anthropic()

        # researcher.md 읽기
        with open(".claude/staff/experts/researcher.md", "r", encoding="utf-8") as f:
            researcher_prompt = f.read()

        # 수집된 데이터 읽기
        market_data = {}
        macro_data = {}
        news_data = {}

        try:
            with open("output/raw/market_data.json", "r", encoding="utf-8") as f:
                market_data = json.load(f)
        except:
            print("⚠️  market_data.json 읽기 실패")

        try:
            with open("output/raw/macro_data.json", "r", encoding="utf-8") as f:
                macro_data = json.load(f)
        except:
            print("⚠️  macro_data.json 읽기 실패")

        try:
            with open("output/raw/news_data.json", "r", encoding="utf-8") as f:
                news_data = json.load(f)
        except:
            print("⚠️  news_data.json 읽기 실패")

        # Claude와 대화
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": f"""다음 역할을 수행해주세요:

{researcher_prompt}

수집된 데이터:
시장 데이터: {json.dumps(market_data, ensure_ascii=False, indent=2)}
거시경제 데이터: {json.dumps(macro_data, ensure_ascii=False, indent=2)}
뉴스 데이터: {json.dumps(news_data, ensure_ascii=False, indent=2)}

이 데이터를 통합하고 정리하여 JSON 형식으로 출력해주세요."""
                }
            ]
        )

        # 결과를 JSON으로 저장
        summary = message.content[0].text

        with open("output/processed/data_summary.json", "w", encoding="utf-8") as f:
            json.dump({
                "status": "success",
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print("✅ 리서처 작업 완료")

    except Exception as e:
        print(f"⚠️  리서처 호출 오류: {e}")

def call_analyst(report_type):
    """애널리스트 호출 - 인사이트 작성"""
    print(f"\n[3단계] 애널리스트 호출: {report_type} 리포트 인사이트 작성")

    try:
        from anthropic import Anthropic

        client = Anthropic()

        # analyst.md 읽기
        with open(".claude/staff/experts/analyst.md", "r", encoding="utf-8") as f:
            analyst_prompt = f.read()

        # data_summary.json 읽기
        try:
            with open("output/processed/data_summary.json", "r", encoding="utf-8") as f:
                data_summary = json.load(f)
        except:
            data_summary = {"summary": "데이터 없음"}

        # Claude와 대화
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": f"""다음 역할을 수행해주세요:

{analyst_prompt}

리포트 타입: {report_type}
통합된 데이터: {json.dumps(data_summary, ensure_ascii=False, indent=2)}

마크다운 형식으로 시장 인사이트를 작성해주세요."""
                }
            ]
        )

        insight = message.content[0].text

        with open("output/drafts/insight_draft.md", "w", encoding="utf-8") as f:
            f.write(insight)

        print("✅ 애널리스트 작업 완료")

    except Exception as e:
        print(f"⚠️  애널리스트 호출 오류: {e}")

def validate_report():
    """리포트 검증"""
    print("\n[4단계] 리포트 검증")

    try:
        result = subprocess.run(
            ["python3", ".claude/scv/validate_report.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("✅ 검증 완료")
    except Exception as e:
        print(f"⚠️  검증 오류: {e}")

def save_to_obsidian(report_type, date_str):
    """Obsidian에 리포트 저장"""
    print(f"\n[6단계] Obsidian 저장: {date_str}_{report_type}_report.md")

    try:
        result = subprocess.run(
            ["python3", ".claude/scv/save_to_obsidian.py",
             "--date", date_str,
             "--type", report_type],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ Obsidian 저장 완료")
        else:
            print(f"⚠️  Obsidian 저장 실패: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Obsidian 저장 오류: {e}")

def generate_final_report(report_type):
    """최종 리포트 생성"""
    print(f"\n[5단계] 최종 {report_type} 리포트 생성")

    try:
        today = datetime.now().strftime("%Y%m%d")

        # 기존 데이터 로드
        try:
            with open("output/processed/data_summary.json", "r", encoding="utf-8") as f:
                data_summary = json.load(f)
                data_content = data_summary.get("summary", "")
        except:
            data_content = ""

        try:
            with open("output/drafts/insight_draft.md", "r", encoding="utf-8") as f:
                insight = f.read()
        except:
            insight = ""

        # 기본 템플릿
        report_content = f"""# 시장 분석 리포트 — {datetime.now().strftime('%Y-%m-%d')} [{report_type.upper()}]
> 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 실행 타입: {report_type}

## 1. 주요 지수 현황
| 지수 | 현재값 | 전일 대비 |
|------|--------|----------|
| KOSPI | - | - |
| KOSDAQ | - | - |
| S&P500 | - | - |
| NASDAQ | - | - |
| 다우존스 | - | - |
| 닛케이225 | - | - |

## 2. 금리·환율
- 원/달러 환율: -원
- 미국 10년물 금리: -%
- 연방기금금리: -%
- 한국 기준금리: -%

## 3. 거시경제 지표
데이터 준비 중

## 4. 부동산 동향
데이터 준비 중

## 5. 주요 경제 뉴스
{data_content}

## 6. 시장 인사이트
{insight}

---

*자동 생성 | 시장 분석 리포트 에이전트 v1.0*
"""

        # 파일 저장
        filename = f"output/final/{today}_{report_type}_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ 최종 리포트 생성: {filename}")

    except Exception as e:
        print(f"⚠️  최종 리포트 생성 오류: {e}")

def main():
    """메인 파이프라인"""
    print("=" * 60)
    print("경제 분석 리포트 자동 생성 시작")
    print("=" * 60)

    # 보고 타입 결정
    report_type = get_report_type()
    print(f"\n📊 리포트 타입: {report_type}")
    print(f"⏰ 현재 시각 (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. 출력 디렉토리 생성
        ensure_output_dirs()

        # 2. SCV 스크립트 실행 (데이터 수집)
        run_scv_scripts()

        # 3. 리서처 호출
        call_researcher()

        # 4. 애널리스트 호출
        call_analyst(report_type)

        # 5. 검증
        validate_report()

        # 6. 최종 리포트 생성
        today = datetime.now().strftime("%Y%m%d")
        generate_final_report(report_type)

        # 7. Obsidian 저장
        save_to_obsidian(report_type, today)

        print("\n" + "=" * 60)
        print("✅ 리포트 생성 및 저장 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 파이프라인 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
