# Pacific SOE Fiscal Risk Monitor (Streamlit 버전)

앞서 만든 대시보드 페이지를 파이썬(Streamlit + Plotly)으로 옮긴 코드입니다.
World Bank 정책노트 *Between Necessity and Risk*의 공개 수치로 만든 예시이며, 월드뱅크 공식 자료가 아닙니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 http://localhost:8501 로 접속하세요.

## 파일 구성

- `app.py` — 대시보드 전체 코드 (데이터, 색상, 차트, 화면 구성)
- `.streamlit/config.toml` — Streamlit 위젯에 월드뱅크 색상 테마 적용. app.py와 같은 폴더에 두세요.
- `requirements.txt` — 테스트한 라이브러리 버전 (Python 3.10 이상 권장)

## 수정할 때

- 논문 수치: `app.py`의 `DATA` 섹션 (`SECTORS`, `Z_BY_SECTOR`, `COUNTRIES` 등)
- 색상: `COLOURS` 섹션 (네이비 #002244, 블루 #009FDA)
- 계산식: `z_score()`, `injection()` 함수와 `SHOCK_DISASTER`, `SHOCK_FX` 계수
- 계산기 프리셋(`PRESETS`)과 트리거 규칙(`TRIGGERS`)은 설명용 예시 값입니다.

## 원본 페이지와 다른 점

- 다크 모드는 없습니다 (라이트 테마 고정).
- 상단 메뉴는 스크롤 시 고정되지 않습니다.
- "Show table"은 각 차트 아래 펼치기 메뉴로 구현했습니다.
