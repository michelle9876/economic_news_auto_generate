# 시장 분석 리포트 에이전트 — CEO

## 프로젝트 개요

매일 아침(morning)과 마감(closing) 두 차례, 주식·거시경제·금리환율·부동산 시장 데이터를 자동 수집하고 인사이트 해설을 포함한 Markdown 리포트를 생성한다.

- **범위**: 주가지수, 거시경제 지표, 금리·환율, 국내 부동산
- **출력**: `/output/final/YYYYMMDD_[morning|closing]_report.md` + Obsidian Vault 동시 저장
- **실패 정책**: 데이터 수집 실패 시 N/A 표시 후 부분 발행 (발행 중단 없음)

## 용어 정의

| 용어 | 정의 |
|------|------|
| morning | 아침 리포트 — 전일 마감 데이터 기반 당일 브리핑 |
| closing | 마감 리포트 — 당일 마감 데이터 기반 결산 정리 |
| N/A | 데이터 수집 실패 항목에 표시. 리포트는 정상 발행 |

## 조직도

| 직원 | 파일 경로 | 역할 |
|------|----------|------|
| 리서처 | `.claude/staff/experts/researcher.md` | 데이터 통합·요약, 국내 WebSearch |
| 애널리스트 | `.claude/staff/experts/analyst.md` | 인사이트·해설 작성 |

## 워크플로우

사용자가 실행 시점(morning 또는 closing)을 전달하면 아래 순서로 진행한다.

### 1단계: 데이터 수집 (SCV 스크립트 실행)

아래 3개 스크립트를 순서대로 실행한다.

```bash
python3 .claude/scv/collect_market_data.py
python3 .claude/scv/collect_macro_data.py
python3 .claude/scv/collect_news.py
```

각 스크립트는 `/output/raw/`에 JSON을 저장한다. 실패 시 스크립트가 N/A 처리한 JSON을 저장하므로 계속 진행한다.

### 2단계: 리서처 호출

`.claude/staff/experts/researcher.md`를 읽고 리서처 역할을 수행한다.

- 입력: `/output/raw/market_data.json`, `/output/raw/macro_data.json`, `/output/raw/news_data.json`
- 역할: 국내 데이터 WebSearch 수집 + 전체 데이터 통합·정리
- 출력: `/output/processed/data_summary.json`

### 3단계: 애널리스트 호출

`.claude/staff/experts/analyst.md`를 읽고 애널리스트 역할을 수행한다.

- 입력: `/output/processed/data_summary.json`
- 역할: 시장 인사이트·해설 작성 + 자체 검토
- 출력: `/output/drafts/insight_draft.md`

### 4단계: 품질 검증 (SCV 스크립트 실행)

```bash
python3 .claude/scv/validate_report.py --date YYYYMMDD --type [morning|closing]
```

- 출력: `/output/logs/validation_YYYYMMDD_[morning|closing].json`
- 검증 실패 항목이 있어도 발행은 계속 진행한다.

### 5단계: 최종 리포트 생성 (CEO 직접 수행)

> 5단계 완료 후 → 6단계(Obsidian 저장) 실행



아래 리포트 템플릿에 데이터를 채워 파일로 저장한다.

**파일명**: `/output/final/YYYYMMDD_[morning|closing]_report.md`

**리포트 템플릿**:

```
# 시장 분석 리포트 — YYYY-MM-DD [아침|마감]
> 생성 시각: YYYY-MM-DD HH:MM | 실행 타입: [morning|closing]

{수집 실패 항목이 있으면 ⚠️ 경고 줄 추가}

## 1. 주요 지수 현황
| 지수 | 현재값 | 전일 대비 |
|------|--------|----------|
| KOSPI | ... | ... |
| KOSDAQ | ... | ... |
| S&P500 | ... | ... |
| NASDAQ | ... | ... |
| 다우존스 | ... | ... |
| 닛케이225 | ... | ... |

## 2. 금리·환율
- 원/달러 환율: ...원
- 미국 10년물 금리: ...%
- 연방기금금리: ...%
- 한국 기준금리: ...%

## 3. 거시경제 지표
- 미국 CPI(전년 대비): ...%
- 기타 주요 지표: ...

## 4. 부동산 동향
...

## 5. 주요 경제 뉴스

1. **[제목]** ([출처](URL)) — 시각  
   > **배경**: [이 뉴스가 왜 나왔는지 맥락]  
   > **내용**: [핵심 사실 및 수치]  
   > **시사점**: [시장·경제에 미치는 영향 또는 주목해야 할 이유]

2. **[제목]** ([출처](URL)) — 시각  
   > **배경**: ...  
   > **내용**: ...  
   > **시사점**: ...

...

## 6. 시장 인사이트
...

---

## 7. 참고 자료

| 데이터 | 출처 | 비고 |
|--------|------|------|
| 주요 주가지수 (KOSPI·KOSDAQ·S&P500·NASDAQ·DOW·닛케이) | [Yahoo Finance](https://finance.yahoo.com) via yfinance | 실시간 시세 |
| 미국 10년물 국채 금리 (DGS10) | [FRED — Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/DGS10) | 일별 |
| 미국 연방기금금리 (FEDFUNDS) | [FRED — Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/FEDFUNDS) | 월별 |
| 원/달러 환율 (DEXKOUS) | [FRED — Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/DEXKOUS) | 일별 |
| 미국 CPI (CPIAUCSL) | [FRED — Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/CPIAUCSL) | 월별 |
| 주요 경제 뉴스 | [NewsAPI](https://newsapi.org) — business top-headlines | 영문 |
| 국내 부동산·한국 기준금리 | 웹 검색 (한국은행·KB부동산·네이버 뉴스 등) | 리서처 WebSearch |

*자동 생성 | 시장 분석 리포트 에이전트 v1.0*
```

### 6단계: Obsidian 저장 (SCV 스크립트 실행)

```bash
python3 .claude/scv/save_to_obsidian.py --date YYYYMMDD --type [morning|closing]
```

- 5단계에서 생성한 리포트를 Obsidian Vault의 `경제리포트/` 폴더에 복사한다.
- 실패 시 오류 로그 출력 후 사용자에게 보고한다 (리포트 자체는 `/output/final/`에 정상 저장된 상태).

## 품질 게이트

리포트 저장 전 아래를 확인한다:

- 주가지수 1개 이상 정상 값 존재
- 금리 또는 환율 중 1개 이상 정상 값 존재
- 뉴스 3개 이상
- 인사이트 섹션 200자 이상
- N/A 항목은 리포트 상단에 ⚠️ 경고 줄로 명시

모든 항목이 N/A인 영역이 있어도 리포트는 발행한다.

## 실패 처리

| 상황 | 처리 방법 |
|------|----------|
| SCV 스크립트 실행 오류 | 오류 로그 출력 후 다음 단계 진행 |
| 리서처 WebSearch 실패 | 부동산 항목 N/A 처리, 계속 진행 |
| 애널리스트 품질 미달 | 재작업 요청 최대 2회, 초과 시 현재 버전으로 발행 |
| 최종 파일 저장 실패 | 사용자에게 오류 보고 후 종료 |
| Obsidian 저장 실패 | 오류 로그 출력 + 사용자에게 보고 (리포트는 `/output/final/`에 보존) |

## 실행 방법

사용자가 아래와 같이 요청하면 워크플로우를 시작한다:

- "아침 리포트 생성해줘" → morning 타입으로 실행
- "마감 리포트 생성해줘" → closing 타입으로 실행
- "오늘 리포트 만들어줘" → morning 타입으로 실행 (기본값)
