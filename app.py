import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import ta

# Configuração da página
st.set_page_config(
    page_title="Painel de Análise Técnica do Bitcoin",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado com cores melhoradas
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
        background-color: #0e1117;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #1e2530 0%, #2d3748 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3d4758;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stMetric label {
        color: #a0aec0 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    h1 {
        color: #f7931a !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    .stSelectbox label, .stCheckbox label, .stSlider label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #2d3748 !important;
        border-color: #4a5568 !important;
        color: #ffffff !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #f7931a 0%, #ff9f1a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(247, 147, 26, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff9f1a 0%, #f7931a 100%);
        box-shadow: 0 6px 8px rgba(247, 147, 26, 0.4);
        transform: translateY(-2px);
    }
    
    .success-box {
        background-color: #1a472a;
        border-left: 4px solid #22c55e;
        padding: 15px;
        border-radius: 5px;
        color: #86efac;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #4a1a1a;
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 5px;
        color: #fca5a5;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #4a3a1a;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 5px;
        color: #fcd34d;
        margin: 10px 0;
    }
    
    .info-box {
        background-color: #1a3a4a;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 5px;
        color: #93c5fd;
        margin: 10px 0;
    }
    
    .analysis-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
        border: 2px solid #3b82f6;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.2);
    }
    
    .analysis-header {
        color: #60a5fa;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    .analysis-content {
        color: #e2e8f0;
        font-size: 16px;
        line-height: 1.8;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #2d1b4e 0%, #3d2b5e 100%);
        border: 2px solid #8b5cf6;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 6px 12px rgba(139, 92, 246, 0.2);
    }
    
    .prediction-title {
        color: #a78bfa;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .prediction-text {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.6;
    }
    
    hr {
        border-color: #4a5568 !important;
        margin: 30px 0;
    }
    
    .sidebar .sidebar-content {
        background-color: #1a202c;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a202c;
    }
    
    .stDataFrame {
        background-color: #2d3748;
        border-radius: 10px;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Título com efeito gradiente
st.markdown("""
    <h1 style='text-align: center; font-size: 48px; margin-bottom: 10px;'>
        ₿ Painel de Análise Técnica do Bitcoin
    </h1>
    """, unsafe_allow_html=True)
st.markdown("---")

# Barra lateral com estilo melhorado
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    # Seleção de período
    period_options = {
        "1 Mês": "1mo",
        "3 Meses": "3mo",
        "6 Meses": "6mo",
        "1 Ano": "1y",
        "2 Anos": "2y",
        "5 Anos": "5y",
        "Máximo": "max"
    }
    
    selected_period = st.selectbox(
        "📅 Selecionar Período",
        options=list(period_options.keys()),
        index=3
    )
    
    # Seleção de intervalo
    interval_options = {
        "1 Dia": "1d",
        "1 Semana": "1wk",
        "1 Mês": "1mo"
    }
    
    selected_interval = st.selectbox(
        "⏱️ Selecionar Intervalo",
        options=list(interval_options.keys()),
        index=0
    )
    
    # Indicadores técnicos
    st.markdown("---")
    st.markdown("### 📊 Indicadores Técnicos")
    show_sma = st.checkbox("Média Móvel Simples (SMA)", value=True)
    show_ema = st.checkbox("Média Móvel Exponencial (EMA)", value=True)
    show_bb = st.checkbox("Bandas de Bollinger", value=True)
    show_rsi = st.checkbox("RSI", value=True)
    show_macd = st.checkbox("MACD", value=True)
    show_volume = st.checkbox("Volume", value=True)
    
    # Períodos das médias móveis
    if show_sma or show_ema:
        st.markdown("---")
        st.markdown("### 📈 Períodos das MAs")
        ma_short = st.slider("Período Curto", 5, 50, 20)
        ma_long = st.slider("Período Longo", 50, 200, 50)

# Função para buscar dados do Bitcoin
@st.cache_data(ttl=300)
def get_bitcoin_data(period, interval):
    try:
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period=period, interval=interval)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return None

# Função para calcular indicadores técnicos
def calculate_indicators(df, ma_short=20, ma_long=50):
    if df is None or df.empty:
        return df
    
    # Médias Móveis Simples
    df['SMA_short'] = ta.trend.sma_indicator(df['Close'], window=ma_short)
    df['SMA_long'] = ta.trend.sma_indicator(df['Close'], window=ma_long)
    
    # Médias Móveis Exponenciais
    df['EMA_short'] = ta.trend.ema_indicator(df['Close'], window=ma_short)
    df['EMA_long'] = ta.trend.ema_indicator(df['Close'], window=ma_long)
    
    # Bandas de Bollinger
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_upper'] = bollinger.bollinger_hband()
    df['BB_middle'] = bollinger.bollinger_mavg()
    df['BB_lower'] = bollinger.bollinger_lband()
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    
    # Indicadores de volume
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    
    return df

# Função para gerar análise de mercado
def generate_market_analysis(df, ma_short, ma_long):
    if df is None or df.empty:
        return None
    
    analysis = {
        'trend': '',
        'momentum': '',
        'volatility': '',
        'volume': '',
        'prediction': '',
        'key_levels': {},
        'signals': []
    }
    
    # Obter valores mais recentes
    current_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
    macd = df['MACD'].iloc[-1] if not pd.isna(df['MACD'].iloc[-1]) else 0
    macd_signal = df['MACD_signal'].iloc[-1] if not pd.isna(df['MACD_signal'].iloc[-1]) else 0
    sma_short = df['SMA_short'].iloc[-1] if not pd.isna(df['SMA_short'].iloc[-1]) else current_price
    sma_long = df['SMA_long'].iloc[-1] if not pd.isna(df['SMA_long'].iloc[-1]) else current_price
    bb_upper = df['BB_upper'].iloc[-1] if not pd.isna(df['BB_upper'].iloc[-1]) else current_price * 1.02
    bb_lower = df['BB_lower'].iloc[-1] if not pd.isna(df['BB_lower'].iloc[-1]) else current_price * 0.98
    
    # Calcular mudanças de preço
    price_change_7d = ((current_price - df['Close'].iloc[-7]) / df['Close'].iloc[-7] * 100) if len(df) >= 7 else 0
    price_change_30d = ((current_price - df['Close'].iloc[-30]) / df['Close'].iloc[-30] * 100) if len(df) >= 30 else 0
    
    # Análise de Tendência
    if sma_short > sma_long:
        if price_change_7d > 5:
            analysis['trend'] = "Fortemente Altista"
            analysis['signals'].append("🚀 Forte tendência de alta confirmada")
        else:
            analysis['trend'] = "Altista"
            analysis['signals'].append("📈 Tendência de alta em progresso")
    else:
        if price_change_7d < -5:
            analysis['trend'] = "Fortemente Baixista"
            analysis['signals'].append("⚠️ Forte tendência de baixa detectada")
        else:
            analysis['trend'] = "Baixista"
            analysis['signals'].append("📉 Tendência de baixa em progresso")
    
    # Análise de Momentum
    if rsi > 70:
        analysis['momentum'] = "Sobrecomprado"
        analysis['signals'].append("⚠️ RSI indica condições de sobrecompra - possível correção à frente")
    elif rsi < 30:
        analysis['momentum'] = "Sobrevendido"
        analysis['signals'].append("💡 RSI indica condições de sobrevenda - possível recuperação esperada")
    elif 45 <= rsi <= 55:
        analysis['momentum'] = "Neutro"
        analysis['signals'].append("⚖️ Momentum está neutro - aguardando direção")
    elif rsi > 55:
        analysis['momentum'] = "Altista"
        analysis['signals'].append("✅ Momentum positivo em construção")
    else:
        analysis['momentum'] = "Baixista"
        analysis['signals'].append("⚠️ Momentum negativo presente")
    
    # Análise MACD
    if macd > macd_signal:
        if macd > 0:
            analysis['signals'].append("🟢 MACD cruzamento altista - sinal de compra ativo")
        else:
            analysis['signals'].append("🟡 MACD virando altista - sinal de compra inicial")
    else:
        if macd < 0:
            analysis['signals'].append("🔴 MACD cruzamento baixista - sinal de venda ativo")
        else:
            analysis['signals'].append("🟠 MACD virando baixista - cautela aconselhada")
    
    # Análise de Volatilidade
    bb_width = ((bb_upper - bb_lower) / current_price) * 100
    if bb_width > 10:
        analysis['volatility'] = "Alta"
        analysis['signals'].append("🌊 Alta volatilidade detectada - espere grandes oscilações de preço")
    elif bb_width < 5:
        analysis['volatility'] = "Baixa"
        analysis['signals'].append("😴 Baixa volatilidade - possível rompimento chegando")
    else:
        analysis['volatility'] = "Moderada"
    
    # Posição nas Bandas de Bollinger
    if current_price > bb_upper:
        analysis['signals'].append("⚠️ Preço acima da Banda de Bollinger superior - sobreestendido")
    elif current_price < bb_lower:
        analysis['signals'].append("💡 Preço abaixo da Banda de Bollinger inferior - possível reversão")
    
    # Análise de Volume
    avg_volume = df['Volume'].tail(20).mean()
    current_volume = df['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    if volume_ratio > 1.5:
        analysis['volume'] = "Alto"
        analysis['signals'].append("📊 Aumento de volume detectado - forte convicção no movimento atual")
    elif volume_ratio < 0.5:
        analysis['volume'] = "Baixo"
        analysis['signals'].append("📉 Volume baixo - falta de convicção, tendência pode ser fraca")
    else:
        analysis['volume'] = "Normal"
    
    # Níveis Chave
    recent_high = df['High'].tail(30).max()
    recent_low = df['Low'].tail(30).min()
    analysis['key_levels'] = {
        'resistance': recent_high,
        'support': recent_low,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower
    }
    
    # Gerar Previsão
    bullish_signals = sum([
        sma_short > sma_long,
        rsi < 70 and rsi > 45,
        macd > macd_signal,
        price_change_7d > 0,
        current_price > bb_lower
    ])
    
    if bullish_signals >= 4:
        analysis['prediction'] = "Forte Compra"
        analysis['outlook'] = f"Com base nos indicadores técnicos, o Bitcoin mostra forte momentum altista. O preço está atualmente em ${current_price:,.2f} com múltiplos indicadores sugerindo movimento ascendente. A resistência chave está em ${recent_high:,.2f}. Se este nível for rompido, podemos ver ganhos adicionais em direção a ${recent_high * 1.05:,.2f}."
    elif bullish_signals >= 3:
        analysis['prediction'] = "Compra"
        analysis['outlook'] = f"O Bitcoin está mostrando sinais positivos com o preço atual em ${current_price:,.2f}. A tendência é favorável, embora alguma cautela seja justificada. Observe o rompimento acima de ${recent_high:,.2f} para confirmação da continuação da tendência de alta."
    elif bullish_signals == 2:
        analysis['prediction'] = "Manter"
        analysis['outlook'] = f"O Bitcoin está em fase de consolidação em ${current_price:,.2f}. Sinais mistos sugerem aguardar por direção mais clara. Níveis chave a observar: suporte em ${recent_low:,.2f} e resistência em ${recent_high:,.2f}."
    elif bullish_signals == 1:
        analysis['prediction'] = "Venda"
        analysis['outlook'] = f"Indicadores técnicos sugerem fraqueza na ação de preço do Bitcoin em ${current_price:,.2f}. Considere reduzir exposição. O suporte crítico em ${recent_low:,.2f} deve se manter para prevenir declínio adicional."
    else:
        analysis['prediction'] = "Forte Venda"
        analysis['outlook'] = f"Múltiplos sinais baixistas detectados com Bitcoin em ${current_price:,.2f}. O risco de queda está elevado. Se o suporte em ${recent_low:,.2f} for rompido, espere declínio adicional em direção a ${recent_low * 0.95:,.2f}."
    
    return analysis

# Buscar dados
with st.spinner("🔄 Buscando dados do Bitcoin..."):
    df = get_bitcoin_data(period_options[selected_period], interval_options[selected_interval])

if df is not None and not df.empty:
    # Calcular indicadores
    df = calculate_indicators(df, ma_short, ma_long)
    
    # Preço atual e métricas
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # Exibir métricas com estilo melhorado
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💰 Preço Atual",
            f"${current_price:,.2f}",
            f"{price_change_pct:+.2f}%"
        )
    
    with col2:
        st.metric(
            "📈 Máxima 24h",
            f"${df['High'].iloc[-1]:,.2f}"
        )
    
    with col3:
        st.metric(
            "📉 Mínima 24h",
            f"${df['Low'].iloc[-1]:,.2f}"
        )
    
    with col4:
        volume_millions = df['Volume'].iloc[-1] / 1_000_000
        st.metric(
            "📊 Volume",
            f"{volume_millions:.2f}M"
        )
    
    with col5:
        if not pd.isna(df['RSI'].iloc[-1]):
            rsi_value = df['RSI'].iloc[-1]
            rsi_status = "Sobrecomprado" if rsi_value > 70 else "Sobrevendido" if rsi_value < 30 else "Neutro"
            st.metric(
                "🎯 RSI",
                f"{rsi_value:.2f}",
                rsi_status
            )
    
    st.markdown("---")
    
    # Gerar Análise de Mercado
    market_analysis = generate_market_analysis(df, ma_short, ma_long)
    
    # Exibir Seção de Análise IA
    if market_analysis:
        st.markdown("## 🤖 Análise de Mercado com IA")
        
        # Caixa de Análise Principal
        st.markdown(f"""
        <div class="analysis-box">
            <div class="analysis-header">
                🎯 Avaliação Atual do Mercado
            </div>
            <div class="analysis-content">
                <p><strong>Perspectiva Geral:</strong> {market_analysis['prediction']}</p>
                <p>{market_analysis['outlook']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Previsões Detalhadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="prediction-title">📊 Resumo Técnico</div>
                <div class="prediction-text">
                    <p><strong>Tendência:</strong> {market_analysis['trend']}</p>
                    <p><strong>Momentum:</strong> {market_analysis['momentum']}</p>
                    <p><strong>Volatilidade:</strong> {market_analysis['volatility']}</p>
                    <p><strong>Volume:</strong> {market_analysis['volume']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="prediction-title">🎯 Níveis de Preço Chave</div>
                <div class="prediction-text">
                    <p><strong>Resistência:</strong> ${market_analysis['key_levels']['resistance']:,.2f}</p>
                    <p><strong>Suporte:</strong> ${market_analysis['key_levels']['support']:,.2f}</p>
                    <p><strong>BB Superior:</strong> ${market_analysis['key_levels']['bb_upper']:,.2f}</p>
                    <p><strong>BB Inferior:</strong> ${market_analysis['key_levels']['bb_lower']:,.2f}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sinais Chave
        st.markdown("### 🔔 Sinais de Negociação Chave")
        for signal in market_analysis['signals']:
            st.markdown(f"- {signal}")
        
        st.markdown("---")
    
    # Criar gráfico principal com tema escuro
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.2, 0.15, 0.15],
        subplot_titles=('Gráfico de Preços', 'Volume', 'RSI', 'MACD')
    )
    
    # Gráfico de velas
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='BTC-USD',
            increasing_line_color='#22c55e',
            decreasing_line_color='#ef4444',
            increasing_fillcolor='#22c55e',
            decreasing_fillcolor='#ef4444'
        ),
        row=1, col=1
    )
    
    # Adicionar médias móveis com cores melhores
    if show_sma:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_short'],
                name=f'SMA {ma_short}',
                line=dict(color='#3b82f6', width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_long'],
                name=f'SMA {ma_long}',
                line=dict(color='#f59e0b', width=2)
            ),
            row=1, col=1
        )
    
    if show_ema:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA_short'],
                name=f'EMA {ma_short}',
                line=dict(color='#8b5cf6', width=2, dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA_long'],
                name=f'EMA {ma_long}',
                line=dict(color='#ec4899', width=2, dash='dash')
            ),
            row=1, col=1
        )
    
    # Adicionar Bandas de Bollinger
    if show_bb:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_upper'],
                name='BB Superior',
                line=dict(color='#64748b', width=1),
                opacity=0.5
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_lower'],
                name='BB Inferior',
                line=dict(color='#64748b', width=1),
                fill='tonexty',
                fillcolor='rgba(100, 116, 139, 0.1)',
                opacity=0.5
            ),
            row=1, col=1
        )
    
    # Volume com cores gradientes
    if show_volume:
        colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#22c55e' 
                  for i in range(len(df))]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.6
            ),
            row=2, col=1
        )
    
    # RSI com zonas coloridas
    if show_rsi:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='#8b5cf6', width=2)
            ),
            row=3, col=1
        )
        # Adicionar linhas de sobrecompra/sobrevenda
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.7, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", opacity=0.7, row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#64748b", opacity=0.5, row=3, col=1)
    
    # MACD com cores melhores
    if show_macd:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD'],
                name='MACD',
                line=dict(color='#3b82f6', width=2)
            ),
            row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                name='Sinal',
                line=dict(color='#f59e0b', width=2)
            ),
            row=4, col=1
        )
        # Histograma MACD
        colors_macd = ['#22c55e' if val >= 0 else '#ef4444' for val in df['MACD_diff']]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['MACD_diff'],
                name='Histograma MACD',
                marker_color=colors_macd,
                opacity=0.6
            ),
            row=4, col=1
        )
    
    # Atualizar layout com tema escuro
    fig.update_layout(
        title={
            'text': 'Análise Técnica do Bitcoin',
            'font': {'size': 24, 'color': '#ffffff', 'family': 'Arial Black'}
        },
        xaxis_rangeslider_visible=False,
        height=1000,
        showlegend=True,
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='#e2e8f0'),
        legend=dict(
            bgcolor='rgba(30, 37, 48, 0.8)',
            bordercolor='#4a5568',
            borderwidth=1
        )
    )
    
    # Atualizar rótulos dos eixos y
    fig.update_yaxes(title_text="Preço (USD)", row=1, col=1, gridcolor='#2d3748')
    fig.update_yaxes(title_text="Volume", row=2, col=1, gridcolor='#2d3748')
    fig.update_yaxes(title_text="RSI", row=3, col=1, gridcolor='#2d3748')
    fig.update_yaxes(title_text="MACD", row=4, col=1, gridcolor='#2d3748')
    
    fig.update_xaxes(gridcolor='#2d3748')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sinais de negociação com caixas estilizadas personalizadas
    st.markdown("---")
    st.markdown("## 📊 Sinais de Negociação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 Análise de Tendência")
        if not pd.isna(df['SMA_short'].iloc[-1]) and not pd.isna(df['SMA_long'].iloc[-1]):
            if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1]:
                st.markdown("<div class='success-box'>🟢 <strong>Altista</strong><br>MA Curta > MA Longa</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='error-box'>🔴 <strong>Baixista</strong><br>MA Curta < MA Longa</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Sinal RSI")
        if not pd.isna(df['RSI'].iloc[-1]):
            rsi_current = df['RSI'].iloc[-1]
            if rsi_current > 70:
                st.markdown(f"<div class='warning-box'>⚠️ <strong>Sobrecomprado</strong><br>RSI: {rsi_current:.2f}</div>", unsafe_allow_html=True)
            elif rsi_current < 30:
                st.markdown(f"<div class='info-box'>💡 <strong>Sobrevendido</strong><br>RSI: {rsi_current:.2f}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='success-box'>✅ <strong>Neutro</strong><br>RSI: {rsi_current:.2f}</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("### ⚡ Sinal MACD")
        if not pd.isna(df['MACD'].iloc[-1]) and not pd.isna(df['MACD_signal'].iloc[-1]):
            if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
                st.markdown("<div class='success-box'>🟢 <strong>Altista</strong><br>MACD > Sinal</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='error-box'>🔴 <strong>Baixista</strong><br>MACD < Sinal</div>", unsafe_allow_html=True)
    
    # Seção de análise de preços
    st.markdown("---")
    st.markdown("## 🔮 Análise de Preços")
    
    # Calcular níveis de suporte e resistência
    recent_high = df['High'].tail(30).max()
    recent_low = df['Low'].tail(30).min()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🎯 Resistência 30 Dias", f"${recent_high:,.2f}")
        st.metric("🛡️ Suporte 30 Dias", f"${recent_low:,.2f}")
    
    with col2:
        avg_volume = df['Volume'].tail(30).mean()
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = (current_volume / avg_volume) * 100 if avg_volume > 0 else 0
        st.metric("📊 Volume vs Média 30 Dias", f"{volume_ratio:.2f}%")
        
        volatility = df['Close'].tail(30).std()
        st.metric("📉 Volatilidade 30 Dias", f"${volatility:,.2f}")
    
    # Tabela de dados históricos
    st.markdown("---")
    st.markdown("## 📈 Dados Históricos")
    
    # Seletor de intervalo de datas para tabela
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "📅 Data Inicial",
            value=df.index[-30].date() if len(df) > 30 else df.index[0].date(),
            min_value=df.index[0].date(),
            max_value=df.index[-1].date()
        )
    with col2:
        end_date = st.date_input(
            "📅 Data Final",
            value=df.index[-1].date(),
            min_value=df.index[0].date(),
            max_value=df.index[-1].date()
        )
    
    # Filtrar dados com base no intervalo de datas
    if not df.empty and len(df) > 0:
        try:
            start_date_ts = pd.Timestamp(start_date)
            end_date_ts = pd.Timestamp(end_date)
            
            # Garantir que as datas estejam dentro do intervalo
            if start_date_ts < df.index[0]:
                start_date_ts = df.index[0]
            if end_date_ts > df.index[-1]:
                end_date_ts = df.index[-1]
            
            filtered_df = df.loc[start_date_ts:end_date_ts]
            
            # Exibir tabela
            display_df = filtered_df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            display_df = display_df.round(2)
            display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                display_df.style.format({
                    'Open': '${:,.2f}',
                    'High': '${:,.2f}',
                    'Low': '${:,.2f}',
                    'Close': '${:,.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Botão de download
            csv = filtered_df.to_csv()
            st.download_button(
                label="📥 Baixar Dados em CSV",
                data=csv,
                file_name=f"bitcoin_dados_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Erro ao filtrar dados: {str(e)}")
    else:
        st.warning("Nenhum dado disponível para o intervalo de datas selecionado")
    
else:
    st.error("Não foi possível buscar dados do Bitcoin. Por favor, tente novamente mais tarde.")

# Rodapé
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #a0aec0;'>
        <p style='font-size: 14px;'>📊 Dados fornecidos pelo Yahoo Finance | 🔄 Atualizado a cada 5 minutos</p>
        <p style='font-size: 12px;'><em>⚠️ Este painel é apenas para fins educacionais. Não é aconselhamento financeiro.</em></p>
    </div>
    """, unsafe_allow_html=True)

# Função principal
def main():
    pass

if __name__ == "__main__":
    main()
