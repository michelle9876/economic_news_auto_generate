"""
SCV: save_to_obsidian.py
역할: 최종 리포트를 Obsidian Vault에 복사
실행: python .claude/scv/save_to_obsidian.py --date 20260408 --type morning
출력: Obsidian Vault/경제리포트/YYYYMMDD_[morning|closing]_report.md
"""

import argparse
import shutil
import os
from pathlib import Path


OBSIDIAN_VAULT = Path("/Users/michellekim/Library/CloudStorage/OneDrive-주식회사디노티시아/Documents/Obsidian Vault")
OBSIDIAN_TARGET_DIR = OBSIDIAN_VAULT / "경제리포트"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="날짜 (YYYYMMDD)")
    parser.add_argument("--type", required=True, choices=["morning", "closing"], help="리포트 타입")
    args = parser.parse_args()

    date_str = args.date
    report_type = args.type
    filename = f"{date_str}_{report_type}_report.md"

    src = Path(f"output/final/{filename}")
    dst = OBSIDIAN_TARGET_DIR / filename

    if not src.exists():
        print(f"[오류] 원본 리포트 없음: {src}")
        raise SystemExit(1)

    if not OBSIDIAN_VAULT.exists():
        print(f"[오류] Obsidian Vault를 찾을 수 없음: {OBSIDIAN_VAULT}")
        raise SystemExit(1)

    OBSIDIAN_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[완료] Obsidian 저장 → {dst}")


if __name__ == "__main__":
    main()
