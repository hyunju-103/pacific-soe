# Pacific SOE Fiscal Risk Monitor (Streamlit 버전, 페이지 분리)

World Bank 정책노트 *Between Necessity and Risk*의 공개 수치로 만든 예시 대시보드입니다. 월드뱅크 공식 자료가 아닙니다.
상단 메뉴의 각 항목이 별도 페이지로 열리고, 페이지마다 주소가 따로 있습니다.

| 메뉴 | 주소 |
|---|---|
| Overview | `/` (첫 화면) |
| Sectors | `/sectors` |
| Countries | `/countries` |
| Early warning calculator | `/calculator` |
| Trigger rules | `/triggers` |

예: Streamlit Community Cloud에 올린 주소가 `https://pacific-soe-monitor.streamlit.app`이면 계산기 페이지는 `https://pacific-soe-monitor.streamlit.app/calculator`입니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 파일 구성

```
app.py                  시작 파일: 페이지 설정, 상단 메뉴, 제목 영역, 출처
common.py               공통: 색상, 논문 수치, 계산식, CSS, 차트
views/overview.py       Overview 페이지
views/sectors.py        Sectors 페이지
views/countries.py      Countries 페이지
views/calculator.py     계산기 페이지
views/triggers.py       트리거 규칙 페이지
.streamlit/config.toml  월드뱅크 색상 테마
requirements.txt        라이브러리 버전
```

GitHub에 올릴 때는 `views` 폴더와 `.streamlit` 폴더까지 위 구조 그대로 저장소 맨 위(루트)에 올려야 합니다.

## 수정할 때

- 논문 수치: `common.py`의 `DATA` 섹션
- 색상: `common.py`의 `COLOURS` 섹션 (네이비 #002244, 블루 #009FDA)
- 페이지 순서·이름·주소: `app.py`의 `pages` 목록
- 계산기 프리셋(`PRESETS`)과 트리거 규칙(`TRIGGERS`)은 설명용 예시 값입니다.

계산기 입력값과 Sectors 페이지의 부문 강조 선택은 다른 페이지에 다녀와도 유지됩니다.
