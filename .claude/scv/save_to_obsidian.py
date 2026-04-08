"""
SCV: save_to_obsidian.py
역할: 최종 리포트를 Obsidian Vault에 복사
실행: python .claude/scv/save_to_obsidian.py --date 20260408 --type morning
출력: Obsidian Vault/경제리포트/YYYYMMDD_[morning|closing]_report.md

환경 변수:
  - OBSIDIAN_VAULT_PATH: Obsidian Vault 경로 (선택, 미설정시 기본값 사용)
  - OBSIDIAN_ENABLED: 'true' 또는 'false' (기본값: 'true')
"""

import argparse
import shutil
import os
from pathlib import Path


def get_obsidian_vault():
    """환경변수 또는 기본값에서 Obsidian Vault 경로 획득"""

    # 1. 환경 변수에서 경로 확인
    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    if vault_path:
        return Path(vault_path)

    # 2. 기본값: 로컬 경로
    default_vault = Path("/Users/michellekim/Library/CloudStorage/OneDrive-주식회사디노티시아/Documents/Obsidian Vault")
    return default_vault


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="날짜 (YYYYMMDD)")
    parser.add_argument("--type", required=True, choices=["morning", "closing"], help="리포트 타입")
    args = parser.parse_args()

    date_str = args.date
    report_type = args.type
    filename = f"{date_str}_{report_type}_report.md"

    # Obsidian 저장 활성화 여부
    obsidian_enabled = os.environ.get("OBSIDIAN_ENABLED", "true").lower() == "true"

    if not obsidian_enabled:
        print(f"[INFO] Obsidian 저장이 비활성화됨 (OBSIDIAN_ENABLED=false)")
        print(f"[INFO] 리포트는 /output/final에 저장됨: {filename}")
        return

    src = Path(f"output/final/{filename}")

    # Obsidian Vault 경로 획득
    OBSIDIAN_VAULT = get_obsidian_vault()
    OBSIDIAN_TARGET_DIR = OBSIDIAN_VAULT / "경제리포트"
    dst = OBSIDIAN_TARGET_DIR / filename

    # 원본 파일 확인
    if not src.exists():
        print(f"[오류] 원본 리포트 없음: {src}")
        raise SystemExit(1)

    # Obsidian Vault 확인
    if not OBSIDIAN_VAULT.exists():
        print(f"[경고] Obsidian Vault를 찾을 수 없음: {OBSIDIAN_VAULT}")
        print(f"[경고] Obsidian 저장을 건너뜀. 리포트는 /output/final에만 저장됨")
        print(f"[정보] Obsidian을 사용하려면 OBSIDIAN_VAULT_PATH 환경변수를 설정하세요")
        return

    # Obsidian에 저장
    try:
        OBSIDIAN_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"[완료] Obsidian 저장 → {dst}")
    except Exception as e:
        print(f"[오류] Obsidian 저장 실패: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
