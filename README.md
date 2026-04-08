# 📊 경제 분석 리포트 자동 생성 시스템

## 개요

매일 **아침(morning)과 저녁(closing)** 두 차례 자동으로 경제 분석 리포트를 생성하는 시스템입니다.

- **자동화**: GitHub Actions를 통해 컴퓨터를 끈 상태에서도 자동 실행
- **데이터**: 주가지수, 거시경제 지표, 금리·환율, 부동산, 경제 뉴스 수집
- **출력**: Markdown 형식 리포트 + Obsidian Vault 자동 저장

## 📅 스케줄

| 시간 | 보고 타입 | 설명 |
|------|---------|------|
| **오후 3시 (UTC 6시)** | `morning` | 전일 마감 데이터 기반 당일 브리핑 |
| **다음날 오전 2시 (UTC 17시)** | `closing` | 당일 마감 데이터 기반 결산 정리 |

> ※ 위 시간은 UTC 기준입니다. 한국 시간으로는 UTC+9입니다.

## 🏗️ 파일 구조

```
.
├── CLAUDE.md                          # 에이전트 설계서
├── run_report_pipeline.py             # 메인 파이프라인 (GitHub Actions에서 실행)
├── requirements.txt                   # Python 의존성
│
├── .github/
│   └── workflows/
│       └── generate_reports.yml       # GitHub Actions 워크플로우
│
├── .claude/
│   ├── scv/                           # 데이터 수집 & 처리 스크립트
│   │   ├── collect_market_data.py    # 주가 데이터 수집
│   │   ├── collect_macro_data.py     # 거시경제 지표 수집
│   │   ├── collect_news.py           # 경제 뉴스 수집
│   │   ├── validate_report.py        # 리포트 검증
│   │   └── save_to_obsidian.py       # Obsidian 저장
│   │
│   └── staff/experts/
│       ├── researcher.md              # 리서처 프롬프트
│       └── analyst.md                 # 애널리스트 프롬프트
│
└── output/
    ├── raw/                          # 수집된 원본 데이터
    ├── processed/                    # 처리된 데이터
    ├── drafts/                       # 초안
    ├── final/                        # 최종 리포트 (발행)
    └── logs/                         # 검증 로그
```

## 🚀 파이프라인 흐름

```
매일 아침/저녁 자동 실행
    ↓
[1단계] 데이터 수집
    ├─ collect_market_data.py   (주가지수)
    ├─ collect_macro_data.py    (거시경제)
    └─ collect_news.py          (경제 뉴스)
    ↓
[2단계] 리서처 호출 (Claude API)
    └─ data_summary.json 생성 (데이터 통합 및 요약)
    ↓
[3단계] 애널리스트 호출 (Claude API)
    └─ insight_draft.md 생성 (인사이트 해설)
    ↓
[4단계] 리포트 검증
    └─ validation_YYYYMMDD_[morning|closing].json
    ↓
[5단계] 최종 리포트 생성
    └─ YYYYMMDD_[morning|closing]_report.md
    ↓
[6단계] GitHub 커밋 & 푸시
    └─ 리포트가 GitHub에 자동 저장됨
    ↓
[7단계] Obsidian 저장 (선택)
    └─ Obsidian Vault에도 복사됨
```

## 🔧 설정 방법

### 1. GitHub 리포에 시크릿 설정

GitHub > Settings > Secrets and variables > Actions에서 아래 시크릿을 추가합니다:

| 시크릿 이름 | 설명 | 예시 |
|-----------|------|------|
| `CLAUDE_API_KEY` | Claude API 키 | `sk-ant-...` |
| `NEWSAPI_KEY` | NewsAPI 키 (선택) | `a1b2c3d4e5f6...` |

### 2. 로컬 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 파이프라인 실행
python3 run_report_pipeline.py
```

### 3. 자동화 활성화

GitHub Actions 페이지에서 **"generate_reports"** 워크플로우가 활성화되어 있는지 확인합니다.

## 📝 생성되는 리포트 예시

```markdown
# 시장 분석 리포트 — 2026-04-08 [MORNING]
> 생성 시각: 2026-04-08 15:23 | 실행 타입: morning

## 1. 주요 지수 현황
| 지수 | 현재값 | 전일 대비 |
|------|--------|----------|
| KOSPI | 2,840.52 | +0.45% |
| ...

## 2. 금리·환율
- 원/달러 환율: 1,145.50원
- ...

## 5. 주요 경제 뉴스
...

## 6. 시장 인사이트
...
```

## 🐛 문제 해결

### GitHub Actions 실행 실패

1. **"API Key not found"** 에러
   - GitHub > Settings > Secrets에서 `CLAUDE_API_KEY` 설정 확인

2. **"Module not found"** 에러
   - `requirements.txt`가 최신인지 확인
   - `pip install -r requirements.txt` 로컬에서 재실행

3. **"No data collected"** 경고
   - 네트워크 문제로 데이터 수집 실패
   - 리포트는 부분적으로 N/A 처리되어 발행됨

### 수동 실행

GitHub Actions 페이지에서:
1. **"generate_reports"** 워크플로우 선택
2. **"Run workflow"** 클릭
3. **"Run workflow"** 버튼 다시 클릭

## 📊 모니터링

### GitHub Actions 로그 확인

1. GitHub 리포 > **Actions** 탭
2. **"경제 분석 리포트 자동 생성"** 워크플로우 클릭
3. 최근 실행 기록에서 상태 확인
   - ✅ 초록색: 성공
   - ❌ 빨간색: 실패 (로그 클릭하여 상세 확인)

### 생성된 리포트 확인

- GitHub: `/output/final/` 폴더
- Obsidian: `경제리포트/` 폴더

## 🔐 보안

- API 키는 GitHub Secrets에만 저장 (코드에 노출 안 함)
- `.env` 파일은 `.gitignore`에 등록되어 커밋 안 됨
- 로컬 테스트 시에만 `.env` 파일 사용

## 📚 추가 정보

- 설계 가이드: [CLAUDE.md](./CLAUDE.md)
- 설계서 상세: [설계서_시장분석리포트.md](./설계서_시장분석리포트.md)

---

**마지막 업데이트**: 2026-04-08  
**유지보수**: Michelle Kim
