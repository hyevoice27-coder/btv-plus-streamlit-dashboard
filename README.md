# B tv+ 월별 신작 대시보드

Streamlit 기반의 월별 신작 및 OTT 편성현황 대시보드입니다.

## 데이터 수정

`data/contents.csv`를 엑셀이나 Google Sheets에서 편집한 뒤 같은 이름으로 교체합니다. OTT 제공 여부는 각 서비스 열에 `O` 또는 `X`를 입력합니다.

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포

1. `share.streamlit.io`에서 **Create app**을 선택합니다.
2. 이 GitHub 저장소와 `main` 브랜치를 선택합니다.
3. Entrypoint에 `app.py`를 입력합니다.
4. 원하는 `*.streamlit.app` 주소를 정하고 Deploy를 누릅니다.
