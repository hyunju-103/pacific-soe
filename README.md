# Pacific SOE Fiscal Risk Monitor (Streamlit 버전, 페이지 분리)

World Bank 정책노트 *Between Necessity and Risk*의 공개 수치로만 만든 대시보드입니다. 모든 수치는 논문에서 가져왔고, 월드뱅크 공식 자료는 아닙니다.
제목 아래 탭(Overview · Sectors · Countries · Early warning calculator · Recommendations)이 항상 보이고, 탭을 누르면 해당 페이지로 넘어갑니다. 탭 줄은 스크롤해도 화면 위에 붙어 있고, 페이지마다 주소가 따로 있습니다.

| 탭 | 주소 |
|---|---|
| Overview | `/` (첫 화면) |
| Sectors | `/sectors` |
| Countries | `/countries` |
| Early warning calculator | `/calculator` |
| Recommendations | `/recommendations` |

예: Streamlit Community Cloud에 올린 주소가 `https://pacific-soe-monitor.streamlit.app`이면 계산기 페이지는 `https://pacific-soe-monitor.streamlit.app/calculator`입니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 파일 구성

```
app.py                  시작 파일: 페이지 설정, 제목 영역, 탭 줄, 출처
common.py               공통: 색상, 논문 수치, 계산식, CSS, 차트
views/overview.py       Overview 페이지
views/sectors.py        Sectors 페이지
views/countries.py      Countries 페이지
views/calculator.py     계산기 페이지
views/recommendations.py  논문의 정책 권고 페이지
.streamlit/config.toml  월드뱅크 색상 테마
requirements.txt        라이브러리 버전
```

GitHub에 올릴 때는 `views` 폴더와 `.streamlit` 폴더까지 위 구조 그대로 저장소 맨 위(루트)에 올려야 합니다.

## 수정할 때

- 논문 수치: `common.py`의 `DATA` 섹션
- 색상: `common.py`의 `COLOURS` 섹션 (네이비 #002244, 블루 #009FDA)
- 탭 순서·이름·주소: `app.py`의 `pages` 목록
- 부문 스코어카드의 판정은 논문에 나온 기준(Z″ 구간, 부채/EBITDA, 유동비율 1, 부채/자산 0.5)만 사용합니다.
- 계산기 시작값은 논문 Table 1의 표본 중앙값이고, 총자산 입력은 선택입니다.

계산기 입력값과 Sectors 페이지의 부문 강조 선택은 다른 페이지에 다녀와도 유지됩니다.
