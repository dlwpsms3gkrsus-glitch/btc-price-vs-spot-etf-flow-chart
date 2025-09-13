CryptoFlow Tracker: BTC & ETH Spot ETF Dashboard
<https://dlwpsms3gkrsus-glitch.github.io/btc-price-vs-spot-etf-flow-chart/>

➡️ Live Demo Website 바로가기 <https://dlwpsms3gkrsus-glitch.github.io/btc-price-vs-spot-etf-flow-chart/>

📜 프로젝트 소개 (About The Project)
CryptoFlow Tracker는 비트코인(BTC)과 이더리움(ETH) 현물 ETF의 일일 순유입량(Net Inflow)과 가격 데이터를 시각적으로 추적하고 분석하는 완전 자동화된 웹 대시보드입니다.

이 프로젝트는 매일 자동으로 최신 ETF 유입량 데이터를 수집하고, 이를 가격 데이터와 결합하여 인터랙티브 차트를 생성한 뒤, 웹사이트를 스스로 업데이트합니다. 사용자는 별도의 조작 없이 매일 아침 최신 데이터가 반영된 대시보드를 확인할 수 있습니다.

✨ 주요 기능 (Features)
실시간 데이터 대시보드: CryptoCompare API를 통해 BTC와 ETH의 현재 가격 및 24시간 변동률을 실시간으로 표시합니다.

일일 자동 업데이트: GitHub Actions를 사용하여 매일 한국 시간 오전 9시 10분에 Farside Investors의 ETF 유입량 데이터를 자동으로 스크랩하고, Yahoo Finance의 가격 데이터와 병합합니다.

다이나믹 코인 전환: BTC/ETH 버튼 클릭 한 번으로 헤더의 요약 정보부터 상세 비교 차트까지 모든 데이터가 해당 자산에 맞게 즉시 전환됩니다.

인터랙티브 차트:

실시간 가격 차트: TradingView 위젯을 통해 깔끔하고 반응성이 뛰어난 실시간 가격 차트를 제공합니다.

상세 비교 차트: Plotly로 생성된 상세 차트를 통해 ETF 누적 순유입량과 가격 추이를 비교 분석할 수 있으며, EMA(지수이동평균) 보조지표를 켜고 끌 수 있습니다.

편의 기능: 상세 비교 차트의 전체 화면 보기/닫기(ESC키 지원) 기능, 데이터 원본 사이트 바로가기 등을 제공하여 사용자 경험을 높였습니다.

🛠️ 기술 스택 (Tech Stack)
이 프로젝트는 아래의 기술들을 사용하여 구축되었습니다.

프론트엔드 (Frontend):

HTML, CSS, JavaScript

Font Awesome: 아이콘 라이브러리

TradingView Lightweight Charts: 실시간 가격 차트

자동화 스크립트 (Automation Script):

Python

데이터 수집:

Selenium: Farside Investors 사이트의 동적 데이터 스크레이핑 (봇 탐지 우회)

yfinance: Yahoo Finance의 일별 가격 데이터 수집

데이터 처리: pandas

차트 생성: plotly

자동화 및 배포 (Automation & Deployment):

GitHub Actions: 매일 정해진 시간에 파이썬 스크립트를 실행하고, 변경된 파일을 자동으로 커밋

GitHub Pages: 완성된 웹사이트를 무료로 호스팅하고 사용자에게 제공

⚙️ 자동화 작동 방식 (How It Works)
스케줄 실행: GitHub Actions는 .github/workflows/update_charts.yml 파일에 설정된 스케줄(cron: '10 0 * * *')에 따라 매일 UTC 00:10 (한국 시간 오전 9:10)에 워크플로우를 실행합니다.

데이터 스크레이핑: update_charts.py 스크립트가 실행됩니다.

Selenium의 헤드리스 모드를 사용하여 Farside Investors에 접속, BTC와 ETH의 일일 ETF 유입량 데이터를 스크레이핑합니다.

수집된 데이터를 bitcoin_etf_total_flow.csv와 ethereum_etf_total_flow.csv 파일로 저장합니다.

차트 생성:

yfinance를 통해 최신 가격 데이터를 가져옵니다.

방금 생성된 CSV 파일의 유입량 데이터와 가격 데이터를 병합합니다.

Plotly를 사용하여 graph_btc.html과 graph_eth.html 인터랙티브 차트 파일을 새로 생성(덮어쓰기)합니다.

자동 커밋: GitHub Actions가 새로 생성된 차트 파일과 CSV 파일을 감지하고, "Daily chart and data update"라는 메시지와 함께 저장소에 자동으로 커밋 및 푸시합니다.

웹사이트 반영: GitHub Pages는 저장소의 파일 변경을 감지하고, 몇 분 내로 실제 웹사이트에 최신 차트와 데이터를 반영합니다.
