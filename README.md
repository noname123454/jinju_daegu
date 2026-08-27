# Open-Meteo 날씨 수집

`collect_weather.py`는 Open-Meteo에서 진주시와 대구광역시의 현재 날씨를 가져와 `data/weather.csv`에 누적합니다. Open-Meteo의 기본 최적 모델 선택을 사용합니다.

## 실행

```powershell
python .\collect_weather.py
```

같은 지역과 기상시각(`weather_time_kst`)의 데이터는 다시 저장하지 않습니다. CSV는 UTF-8 BOM 인코딩이므로 Excel에서도 한글 열 수 있습니다.

## CSV 열

- 수집시각(UTC), 기상시각(한국 시간), 지역, 위도, 경도
- 기온, 상대습도, 체감온도, 강수량, 비, 소나기, 적설, 날씨 코드, 운량, 풍속, 풍향, 돌풍

자동 실행과 GitHub 커밋·푸시는 다음 단계에서 설정합니다.
