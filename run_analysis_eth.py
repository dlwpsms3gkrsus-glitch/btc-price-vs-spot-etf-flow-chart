import pandas as pd
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from io import StringIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_etf_flow():
    """
    Farside Investors 웹사이트에서 현물 ETF 유입량 데이터를 스크레이핑하고 정제하여
    데이터프레임으로 반환합니다. (안정성 강화)
    """
    print("▶ 1단계: Farside Investors에서 ETF 유입량 데이터를 스크레이핑합니다...")
    url = "https://farside.co.uk/ethereum-etf-flow-all-data/"
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    options.add_argument('--headless') # GitHub Actions 환경을 위한 헤드리스 모드 활성화
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")# "나는 일반 사용자"임을 알리는 User-Agent 정보 추가
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        print("🤖 브라우저를 실행하여 페이지에 접속합니다. 잠시 기다려주세요...")
        time.sleep(5)
        html = driver.page_source
        
        all_tables = pd.read_html(StringIO(html), flavor='html5lib')
        print(f"페이지에서 총 {len(all_tables)}개의 테이블을 찾았습니다.")

        daily_flow_table = None
        for i, table in enumerate(all_tables):
            columns_str = ' '.join(map(str, table.columns.to_flat_index()))
            first_row_str = ' '.join(map(str, table.iloc[0].values))
            
            if 'Total' in columns_str or 'Total' in first_row_str:
                print(f"✔️ {i+1}번째 테이블에서 'Total' 열을 발견하여 메인 데이터로 선택합니다.")
                daily_flow_table = table
                break
        
        if daily_flow_table is None:
            print("❌ 일일 현금 흐름 데이터 테이블을 찾지 못했습니다.")
            return None
        
        df = daily_flow_table.copy()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        if str(df.columns[0]).strip().lower() == str(df.iloc[0, 0]).strip().lower():
            df = df.iloc[1:].reset_index(drop=True)

        total_flow_df = df.iloc[:, [0, -1]].copy()
        total_flow_df.columns = ['Date', 'Total']
        
        total_flow_df = total_flow_df[total_flow_df['Date'] != 'Total']
        total_flow_df['Total'] = total_flow_df['Total'].astype(str).str.replace('(', '-', regex=False).str.replace(')', '', regex=False)
        total_flow_df['Total'] = pd.to_numeric(total_flow_df['Total'], errors='coerce')
        
        total_flow_df['Date'] = pd.to_datetime(total_flow_df['Date'], errors='coerce')
        total_flow_df.dropna(inplace=True)

        print("✔️ ETF 유입량 데이터 정제 완료.")
        return total_flow_df

    except Exception as e:
        print(f"❌ 스크레이핑 중 오류 발생: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def get_price_data(ticker, start_date):
    """Yahoo Finance에서 특정 티커의 가격 데이터를 가져옵니다."""
    print(f"▶ 2단계: Yahoo Finance에서 '{ticker}' 가격 데이터를 다운로드합니다...")
    try:
        df = yf.download(ticker, start_date, progress=False)
        
        if df.empty:
            print("❌ 가격 데이터를 다운로드하지 못했습니다.")
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df.reset_index(inplace=True)

        print("✔️ 가격 데이터 다운로드 완료.")
        return df
    except Exception as e:
        print(f"❌ 가격 데이터 다운로드 중 오류 발생: {e}")
        return None

def create_chart(price_df, etf_df):
    """가격과 ETF 유입량 데이터를 병합하여 최종 차트를 생성합니다."""
    print("▶ 3단계: 데이터 병합 및 최종 차트 생성을 시작합니다...")
    try:
        merged_df = pd.merge(price_df[['Date', 'Close']], etf_df, on='Date', how='inner')
        merged_df.sort_values('Date', inplace=True)

        merged_df['Cumulative_Flow'] = merged_df['Total'].cumsum()
        
        merged_df['EMA_20'] = merged_df['Close'].ewm(span=20, adjust=False).mean()
        merged_df['EMA_60'] = merged_df['Close'].ewm(span=60, adjust=False).mean()
        merged_df['EMA_120'] = merged_df['Close'].ewm(span=120, adjust=False).mean()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # --- ▼▼▼ [UI 수정] BTC 차트와 색상 통일 ▼▼▼ ---
        fig.add_trace(go.Scatter(x=merged_df['Date'], y=merged_df['Close'], name='ETH Price', line=dict(color='royalblue', width=1.5)), secondary_y=False)
        fig.add_trace(go.Scatter(x=merged_df['Date'], y=merged_df['EMA_20'], name='EMA 20-Day', line=dict(color='black', width=1, dash='dash'), visible='legendonly'), secondary_y=False)
        fig.add_trace(go.Scatter(x=merged_df['Date'], y=merged_df['EMA_60'], name='EMA 60-Day', line=dict(color='green', width=1, dash='dash'), visible='legendonly'), secondary_y=False)
        fig.add_trace(go.Scatter(x=merged_df['Date'], y=merged_df['EMA_120'], name='EMA 120-Day', line=dict(color='red', width=1, dash='dash'), visible='legendonly'), secondary_y=False)
        
        fig.add_trace(go.Scatter(x=merged_df['Date'], y=merged_df['Cumulative_Flow'], name='Cumulative Inflow', line=dict(color='darkorange', width=2)), secondary_y=True)
        # --- ▲▲▲ ---------------------------------- ▲▲▲ ---

        fig.update_layout(
            title_text='<b>ETH Price vs Cumulative Spot ETF Net Inflow</b>',
            # --- ▼▼▼ [UI 수정] BTC 차트와 배경/범례 스타일 통일 ▼▼▼ ---
            plot_bgcolor='#E5ECF6', # 플롯 배경색
            paper_bgcolor='white',  # 전체 배경색
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.02,
                bgcolor='rgba(255, 255, 255, 0.6)',
                bordercolor="Black",
                borderwidth=1
            ),
            # --- ▲▲▲ ------------------------------------------ ▲▲▲ ---
            xaxis=dict(
                rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"), dict(count=3, label="3m", step="month", stepmode="backward"), dict(count=6, label="6m", step="month", stepmode="backward"), dict(step="all")])),
                rangeslider=dict(visible=True), type="date"
            )
        )
        # --- ▼▼▼ [UI 수정] BTC 차트와 축 색상 통일 ▼▼▼ ---
        fig.update_yaxes(title_text='<b>ETH Price (USD)</b>', color='royalblue', secondary_y=False)
        fig.update_yaxes(title_text='<b>ETF Cumulative Net Inflow (US$M)</b>', color='darkorange', secondary_y=True)
        # --- ▲▲▲ ---------------------------------- ▲▲▲ ---

        file_name = 'graph_eth.html'
        fig.write_html(file_name)
        print(f"✅ 최종 그래프 생성 완료! '{file_name}' 파일을 확인해주세요.")

    except Exception as e:
        print(f"❌ 차트 생성 중 오류 발생: {e}")

# --- 메인 실행 블록 ---
if __name__ == '__main__':
    etf_data = scrape_etf_flow()
    price_data = None

    if etf_data is not None and not etf_data.empty:
        etf_data.to_csv('ethereum_etf_total_flow.csv', index=False)
        print("💾 'ethereum_etf_total_flow.csv' 파일 저장 완료.")
        
        start_date = etf_data['Date'].min().strftime('%Y-%m-%d')
        price_data = get_price_data('ETH-USD', start_date)

        if price_data is not None:
            price_data.to_csv('ethereum_price_data.csv', index=False)
            print("💾 'ethereum_price_data.csv' 파일 저장 완료.")
            create_chart(price_data, etf_data)
    else:
        print("ETF 데이터가 없어 분석을 진행할 수 없습니다.")

