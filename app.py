import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="📊 Dashboard de Ciclos do Bitcoin",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #F7931A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .cycle-phase {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        font-size: 1.3rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .accumulation { 
        background: linear-gradient(135deg, #E8F5E8, #C8E6C9); 
        color: #1B5E20; 
        border-left: 5px solid #4CAF50;
    }
    .bull-run { 
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2); 
        color: #E65100; 
        border-left: 5px solid #FF9800;
    }
    .euphoria { 
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2); 
        color: #B71C1C; 
        border-left: 5px solid #F44336;
    }
    .bear-market { 
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB); 
        color: #0D47A1; 
        border-left: 5px solid #2196F3;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .indicator-safe { color: #4CAF50; font-weight: bold; }
    .indicator-warning { color: #FF9800; font-weight: bold; }
    .indicator-danger { color: #F44336; font-weight: bold; }
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Cache otimizado para Streamlit Cloud
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bitcoin_data(period='2y'):
    """Busca dados do Bitcoin com fallback robusto"""
    try:
        btc = yf.Ticker("BTC-USD")
        data = btc.history(period=period, interval='1d')
        
        if data.empty or len(data) < 100:
            raise Exception("Dados insuficientes")
            
        # Calcular médias móveis
        data['MA_50'] = data['Close'].rolling(window=50, min_periods=1).mean()
        data['MA_111'] = data['Close'].rolling(window=111, min_periods=1).mean()
        data['MA_200'] = data['Close'].rolling(window=200, min_periods=1).mean()
        data['MA_350'] = data['Close'].rolling(window=350, min_periods=1).mean()
        data['MA_350_x2'] = data['MA_350'] * 2
        
        st.success("✅ Dados reais carregados com sucesso!")
        return data, True
        
    except Exception as e:
        st.warning(f"⚠️ Usando dados simulados: {str(e)}")
        return generate_simulation_data(period), False

def generate_simulation_data(period='2y'):
    """Gera dados simulados realísticos"""
    days_map = {'1y': 365, '2y': 730, '3y': 1095, '5y': 1825}
    n_days = days_map.get(period, 730)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    np.random.seed(42)  # Reprodutibilidade
    
    # Simular preços com padrão realístico
    base_price = 30000
    prices = []
    current_price = base_price
    
    halving_date = datetime(2024, 4, 20)
    
    for date in dates:
        days_since_halving = (date - halving_date).days
        
        # Fator de crescimento baseado no ciclo
        if days_since_halving < 0:
            growth = np.random.normal(0.0003, 0.03)  # Pré-halving
        elif days_since_halving < 500:
            cycle_boost = min(days_since_halving / 500, 1) * 0.001
            growth = np.random.normal(0.0008 + cycle_boost, 0.04)  # Pós-halving
        else:
            growth = np.random.normal(0.0002, 0.035)  # Estável
        
        current_price *= (1 + growth)
        prices.append(max(current_price, 1000))  # Preço mínimo
    
    # Criar DataFrame
    df = pd.DataFrame(index=dates)
    df['Close'] = prices
    df['High'] = df['Close'] * (1 + np.random.uniform(0, 0.02, len(df)))
    df['Low'] = df['Close'] * (1 - np.random.uniform(0, 0.02, len(df)))
    df['Open'] = df['Close'].shift(1).fillna(df['Close'])
    df['Volume'] = np.random.lognormal(15, 0.2, len(df))
    
    # Médias móveis
    df['MA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['MA_111'] = df['Close'].rolling(window=111, min_periods=1).mean()
    df['MA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
    df['MA_350'] = df['Close'].rolling(window=350, min_periods=1).mean()
    df['MA_350_x2'] = df['MA_350'] * 2
    
    return df

def calculate_indicators(df):
    """Calcula indicadores técnicos"""
    df = df.copy()
    
    # MVRV Z-Score (aproximação)
    ma_365 = df['Close'].rolling(window=365, min_periods=30).mean()
    std_365 = df['Close'].rolling(window=365, min_periods=30).std()
    df['mvrv_zscore'] = (df['Close'] - ma_365) / std_365.replace(0, 1)
    
    # Pi Cycle Top
    df['pi_cycle_signal'] = (df['MA_111'] > df['MA_350_x2']) & df['MA_111'].notna() & df['MA_350_x2'].notna()
    
    # Puell Multiple (aproximação)
    df['puell_multiple'] = df['Close'] / ma_365.replace(0, 1)
    
    # Mayer Multiple
    df['mayer_multiple'] = df['Close'] / df['MA_200'].replace(0, 1)
    
    # Drawdown
    df['ath'] = df['Close'].expanding().max()
    df['drawdown_pct'] = ((df['Close'] / df['ath']) - 1) * 100
    
    return df

def determine_cycle_phase(latest_data):
    """Determina fase do ciclo"""
    try:
        mvrv = latest_data.get('mvrv_zscore', 0)
        pi_cycle = latest_data.get('pi_cycle_signal', False)
        puell = latest_data.get('puell_multiple', 1)
        mayer = latest_data.get('mayer_multiple', 1)
        drawdown = latest_data.get('drawdown_pct', 0)
        
        # Sistema de pontuação
        score = 0
        
        if pd.notna(mvrv):
            if mvrv < -0.5:
                score -= 3
            elif mvrv > 3:
                score += 3
            elif mvrv > 1:
                score += 1
        
        if pi_cycle:
            score += 4
        
        if pd.notna(puell) and puell > 3:
            score += 2
        elif pd.notna(puell) and puell < 0.7:
            score -= 2
        
        if pd.notna(mayer) and mayer > 2:
            score += 2
        elif pd.notna(mayer) and mayer < 0.8:
            score -= 2
        
        if drawdown < -60:
            score -= 3
        elif drawdown < -30:
            score -= 1
        
        # Determinar fase
        if score <= -3:
            return 'accumulation', 'Acumulação - Zona de Compra'
        elif score >= 4:
            return 'euphoria', 'Euforia - Zona de Risco'
        elif score >= 1:
            return 'bull-run', 'Bull Run - Tendência de Alta'
        else:
            return 'bear-market', 'Bear Market - Correção'
            
    except Exception:
        return 'bull-run', 'Bull Run - Tendência de Alta'

def main():
    st.markdown('<h1 class="main-header">₿ Dashboard de Análise de Ciclos do Bitcoin</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    period = st.sidebar.selectbox(
        "📅 Período de Análise",
        ['1y', '2y', '3y', '5y'],
        index=1,
        help="Selecione o período histórico"
    )
    
    show_halvings = st.sidebar.checkbox("📍 Mostrar Halvings", True)
    
    # Disclaimer
    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Aviso:</strong> Dashboard educacional com aproximações dos indicadores on-chain. 
        Para análises profissionais, use APIs especializadas.
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('🔄 Carregando dados do Bitcoin...'):
        df, is_real_data = fetch_bitcoin_data(period)
        if df is not None and not df.empty:
            df = calculate_indicators(df)
        else:
            st.error("❌ Erro ao carregar dados")
            return
    
    # Dados atuais
    latest = df.iloc[-1]
    current_price = latest['Close']
    price_change_24h = ((current_price / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0
    
    # Determinar fase
    phase_key, phase_name = determine_cycle_phase(latest)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Preço Atual</h3>
            <h2>${current_price:,.0f}</h2>
            <p>{'Real' if is_real_data else 'Simulado'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        change_color = "#4CAF50" if price_change_24h >= 0 else "#F44336"
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Variação 24h</h3>
            <h2 style="color: {change_color}">{price_change_24h:+.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        next_halving = datetime(2028, 4, 20)
        days_to_halving = (next_halving - datetime.now()).days
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏰ Próximo Halving</h3>
            <h2>{days_to_halving}</h2>
            <p>dias</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mayer = latest.get('mayer_multiple', 1)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Mayer Multiple</h3>
            <h2>{mayer:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Fase atual
    st.markdown(f"""
    <div class="cycle-phase {phase_key}">
        🎯 <strong>FASE ATUAL:</strong> {phase_name}
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico principal
    st.subheader("📈 Análise Técnica do Bitcoin")
    
    fig_main = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Preço com Médias Móveis e Pi Cycle', 'Volume'),
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2]
    )
    
    # Preço e médias
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name='BTC', 
                  line=dict(color='#F7931A', width=2)),
        row=1, col=1
    )
    
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['MA_111'], name='MA 111', 
                  line=dict(color='#2196F3', width=1)),
        row=1, col=1
    )
    
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['MA_350_x2'], name='MA 350×2 (Pi Cycle)', 
                  line=dict(color='#F44336', width=1, dash='dot')),
        row=1, col=1
    )
    
    # Volume
    fig_main.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', 
               marker_color='rgba(158,158,158,0.3)'),
        row=2, col=1
    )
    
    # Halvings
    if show_halvings:
        halvings = {
            '4º Halving': datetime(2024, 4, 20),
            '3º Halving': datetime(2020, 5, 11),
            '2º Halving': datetime(2016, 7, 9)
        }
        
        for name, date in halvings.items():
            if df.index[0] <= date <= df.index[-1]:
                fig_main.add_vline(
                    x=date, line_dash="dash", line_color="purple",
                    annotation_text=name
                )
    
    fig_main.update_layout(height=600, showlegend=True, hovermode='x unified')
    fig_main.update_yaxes(type="log", title_text="Preço (USD)", row=1, col=1)
    fig_main.update_yaxes(title_text="Volume", row=2, col=1)
    
    st.plotly_chart(fig_main, use_container_width=True)
    
    # Indicadores
    st.subheader("🎯 Indicadores de Ciclo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # MVRV Z-Score
        fig_mvrv = go.Figure()
        fig_mvrv.add_trace(go.Scatter(x=df.index, y=df['mvrv_zscore'], 
                                     name='MVRV Z-Score', line=dict(color='#4CAF50')))
        fig_mvrv.add_hline(y=6, line_dash="dash", line_color="red", 
                          annotation_text="Zona de Risco")
        fig_mvrv.add_hline(y=-0.5, line_dash="dash", line_color="green", 
                          annotation_text="Oportunidade")
        fig_mvrv.update_layout(title="MVRV Z-Score", height=300)
        st.plotly_chart(fig_mvrv, use_container_width=True)
        
        # Puell Multiple
        fig_puell = go.Figure()
        fig_puell.add_trace(go.Scatter(x=df.index, y=df['puell_multiple'], 
                                      name='Puell Multiple', line=dict(color='#9C27B0')))
        fig_puell.add_hline(y=4, line_dash="dash", line_color="red", 
                           annotation_text="Topo Histórico")
        fig_puell.update_layout(title="Puell Multiple", height=300)
        st.plotly_chart(fig_puell, use_container_width=True)
    
    with col2:
        # Pi Cycle
        fig_pi = go.Figure()
        fig_pi.add_trace(go.Scatter(x=df.index, y=df['MA_111'], name='MA 111'))
        fig_pi.add_trace(go.Scatter(x=df.index, y=df['MA_350_x2'], name='MA 350×2'))
        
        # Sinalizar cruzamentos
        crossovers = df[df['pi_cycle_signal']]
        if not crossovers.empty:
            fig_pi.add_trace(go.Scatter(x=crossovers.index, y=crossovers['MA_111'],
                                       mode='markers', name='Pi Cycle Signal',
                                       marker=dict(color='red', size=8)))
        
        fig_pi.update_layout(title="Pi Cycle Top Indicator", height=300)
        st.plotly_chart(fig_pi, use_container_width=True)
        
        # Mayer Multiple
        fig_mayer = go.Figure()
        fig_mayer.add_trace(go.Scatter(x=df.index, y=df['mayer_multiple'], 
                                      name='Mayer Multiple', line=dict(color='#FF5722')))
        fig_mayer.add_hline(y=2.4, line_dash="dash", line_color="orange", 
                           annotation_text="Zona de Atenção")
        fig_mayer.update_layout(title="Mayer Multiple", height=300)
        st.plotly_chart(fig_mayer, use_container_width=True)
    
    # Status dos indicadores
    st.subheader("📊 Status Atual dos Indicadores")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mvrv_current = latest.get('mvrv_zscore', 0)
        if pd.isna(mvrv_current):
            status = "N/A"
            color_class = "indicator-warning"
        elif mvrv_current < 0:
            status = "OPORTUNIDADE"
            color_class = "indicator-safe"
        elif mvrv_current < 3:
            status = "NEUTRO"
            color_class = "indicator-warning"
        else:
            status = "RISCO"
            color_class = "indicator-danger"
        
        st.markdown(f"""
        **MVRV Z-Score:** <span class="{color_class}">{mvrv_current:.2f} - {status}</span>
        
        - < 0: Zona de oportunidade
        - 0-3: Zona neutra
        - > 3: Zona de risco
        """, unsafe_allow_html=True)
    
    with col2:
        pi_current = latest.get('pi_cycle_signal', False)
        pi_status = "🔴 ATIVO" if pi_current else "🟢 INATIVO"
        pi_class = "indicator-danger" if pi_current else "indicator-safe"
        
        st.markdown(f"""
        **Pi Cycle Top:** <span class="{pi_class}">{pi_status}</span>
        
        - Sinal histórico de topo
        - MA 111 > MA 350 × 2
        - Precisão: ~3 dias do pico
        """, unsafe_allow_html=True)
    
    with col3:
        puell_current = latest.get('puell_multiple', 1)
        if pd.isna(puell_current):
            puell_status = "N/A"
            puell_class = "indicator-warning"
        elif puell_current > 4:
            puell_status = "DISTRIBUIÇÃO"
            puell_class = "indicator-danger"
        elif puell_current < 0.5:
            puell_status = "ACUMULAÇÃO"
            puell_class = "indicator-safe"
        else:
            puell_status = "NORMAL"
            puell_class = "indicator-warning"
        
        st.markdown(f"""
        **Puell Multiple:** <span class="{puell_class}">{puell_current:.2f} - {puell_status}</span>
        
        - < 0.5: Acumulação
        - 0.5-4: Normal
        - > 4: Distribuição
        """, unsafe_allow_html=True)
    
    # Estratégia recomendada
    st.subheader("💡 Estratégia Recomendada")
    
    strategies = {
        'accumulation': """
        🟢 **ACUMULAÇÃO - COMPRAR AGRESSIVAMENTE**
        - Implemente DCA semanal/mensal
        - Aproveite quedas >15% para aportes extras
        - Mantenha 80-90% do capital alocado
        - Horizonte: 18-24 meses
        """,
        'bull-run': """
        🟡 **BULL RUN - MANTER POSIÇÕES**
        - Reduza DCA mas mantenha consistência
        - Prepare realizações parciais (10-20%)
        - Monitore indicadores de topo diariamente
        - Risco moderado, volatilidade crescente
        """,
        'euphoria': """
        🔴 **EUFORIA - REALIZAR LUCROS**
        - Venda 30-50% das posições imediatamente
        - Monitore Pi Cycle Top diariamente
        - Prepare-se para bear market iminente
        - Mantenha apenas core de longo prazo (20-30%)
        """,
        'bear-market': """
        🔵 **BEAR MARKET - PACIÊNCIA**
        - Retome DCA gradualmente
        - Aproveite quedas >20% para compras
        - 12-18 meses de lateralização esperada
        - Use tempo para estudar e se preparar
        """
    }
    
    current_strategy = strategies.get(phase_key, strategies['bull-run'])
    st.markdown(current_strategy)
    
    # Tabela de ciclos históricos
    st.subheader("📚 Dados Históricos dos Ciclos")
    
    cycles_data = {
        'Ciclo': ['1º (2009-2012)', '2º (2012-2016)', '3º (2016-2020)', '4º (2020-2024)', 'Atual (2024-?)'],
        'Data do Halving': ['28/11/2012', '09/07/2016', '11/05/2020', '20/04/2024', '~2028'],
        'Preço no Halving': ['$12', '$650', '$8.600', '$64.000', f'${current_price:,.0f}'],
        'Pico Máximo': ['$1.163', '$19.783', '$68.789', 'Em progresso', 'TBD'],
        'Ganho Total': ['9.592%', '3.043%', '800%', 'TBD', 'TBD'],
        'Duração (meses)': ['12', '17', '18', 'TBD', 'TBD']
    }
    
    df_cycles = pd.DataFrame(cycles_data)
    st.dataframe(df_cycles, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    **⚠️ Disclaimer:** Dashboard educacional. Não constitui consultoria financeira. 
    Invista apenas o que pode perder.
    
    **Última atualização:** {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
    
    **Fonte:** {'Yahoo Finance (dados reais)' if is_real_data else 'Simulação baseada em padrões históricos'}
    """)

if __name__ == "__main__":
    main()
