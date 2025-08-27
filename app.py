import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
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

# CSS personalizado para interface atrativa
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
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
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

class BitcoinCycleAnalyzer:
    def __init__(self):
        self.halving_dates = {
            '1º Halving': datetime(2012, 11, 28),
            '2º Halving': datetime(2016, 7, 9),
            '3º Halving': datetime(2020, 5, 11),
            '4º Halving': datetime(2024, 4, 20)
        }
        
    @st.cache_data(ttl=3600)
    def fetch_bitcoin_data(_self, period='5y'):
        """Busca dados históricos reais do Bitcoin"""
        try:
            # Tentar múltiplas fontes
            btc = yf.Ticker("BTC-USD")
            data = btc.history(period=period, interval='1d')
            
            if data.empty:
                raise Exception("Dados do yfinance indisponíveis")
                
            # Calcular médias móveis necessárias
            data['MA_50'] = data['Close'].rolling(window=50, min_periods=1).mean()
            data['MA_111'] = data['Close'].rolling(window=111, min_periods=1).mean()
            data['MA_200'] = data['Close'].rolling(window=200, min_periods=1).mean()
            data['MA_350'] = data['Close'].rolling(window=350, min_periods=1).mean()
            data['MA_350_x2'] = data['MA_350'] * 2
            
            return data
            
        except Exception as e:
            st.error(f"Erro ao buscar dados reais: {e}")
            return _self._generate_simulated_data()
    
    def _generate_simulated_data(self):
        """Gera dados simulados quando APIs falham"""
        st.warning("⚠️ Usando dados simulados devido a falha na API")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 anos
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Simulação realística baseada em padrões históricos
        np.random.seed(42)
        n_days = len(dates)
        
        # Preço base com crescimento exponencial e volatilidade
        price_base = 10000
        growth_rate = 0.0003  # 0.03% daily average
        volatility = 0.04     # 4% daily volatility
        
        # Gerar série de preços com tendência
        returns = np.random.normal(growth_rate, volatility, n_days)
        price_series = price_base * np.exp(np.cumsum(returns))
        
        # Adicionar ciclos de halving
        for i, date in enumerate(dates):
            days_since_halving = min([
                (date - halving_date).days 
                for halving_date in self.halving_dates.values() 
                if date >= halving_date
            ] + [float('inf')])
            
            if days_since_halving < 500:  # 500 dias pós-halving
                cycle_multiplier = 1 + (500 - days_since_halving) / 1000
                price_series[i] *= cycle_multiplier
        
        df = pd.DataFrame(index=dates)
        df['Close'] = price_series
        df['High'] = df['Close'] * (1 + np.random.uniform(0, 0.05, n_days))
        df['Low'] = df['Close'] * (1 - np.random.uniform(0, 0.05, n_days))
        df['Open'] = df['Close'].shift(1).fillna(df['Close'])
        df['Volume'] = np.random.lognormal(15, 0.5, n_days)
        
        # Médias móveis
        df['MA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        df['MA_111'] = df['Close'].rolling(window=111, min_periods=1).mean()
        df['MA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
        df['MA_350'] = df['Close'].rolling(window=350, min_periods=1).mean()
        df['MA_350_x2'] = df['MA_350'] * 2
        
        return df
    
    def calculate_technical_indicators(self, df):
        """Calcula indicadores técnicos e on-chain (aproximados)"""
        df = df.copy()
        
        # MVRV Z-Score (aproximação baseada em volatilidade)
        price_ma_365 = df['Close'].rolling(window=365, min_periods=30).mean()
        price_std_365 = df['Close'].rolling(window=365, min_periods=30).std()
        df['mvrv_zscore'] = (df['Close'] - price_ma_365) / price_std_365.replace(0, np.nan)
        
        # Pi Cycle Top Indicator
        df['pi_cycle_signal'] = df['MA_111'] > df['MA_350_x2']
        
        # Puell Multiple (aproximação)
        # Baseado na relação entre preço atual e média de longo prazo
        df['puell_multiple'] = df['Close'] / df['Close'].rolling(window=365, min_periods=30).mean()
        
        # RHODL Ratio (aproximação baseada em volatilidade)
        short_vol = df['Close'].pct_change().rolling(window=30).std()
        long_vol = df['Close'].pct_change().rolling(window=365).std()
        df['rhodl_ratio'] = (short_vol / long_vol.replace(0, np.nan)) * 10000
        
        # Reserve Risk (aproximação)
        confidence = df['Close'] / df['Close'].rolling(window=365, min_periods=30).mean()
        hodl_confidence = 1 / (df['rhodl_ratio'] / 10000 + 0.1)
        df['reserve_risk'] = confidence / hodl_confidence
        
        # Mayer Multiple
        df['mayer_multiple'] = df['Close'] / df['MA_200']
        
        # Drawdown do ATH
        df['ath'] = df['Close'].expanding().max()
        df['drawdown_pct'] = ((df['Close'] / df['ath']) - 1) * 100
        
        return df
    
    def determine_cycle_phase(self, latest_data):
        """Determina a fase atual do ciclo baseada em múltiplos indicadores"""
        price = latest_data['Close']
        mvrv = latest_data.get('mvrv_zscore', 0)
        pi_cycle = latest_data.get('pi_cycle_signal', False)
        puell = latest_data.get('puell_multiple', 1)
        rhodl = latest_data.get('rhodl_ratio', 0)
        mayer = latest_data.get('mayer_multiple', 1)
        drawdown = latest_data.get('drawdown_pct', 0)
        
        # Sistema de pontuação para determinar fase
        scores = {
            'accumulation': 0,
            'bull-run': 0,
            'euphoria': 0,
            'bear-market': 0
        }
        
        # MVRV Z-Score
        if pd.notna(mvrv):
            if mvrv < -0.5:
                scores['accumulation'] += 3
            elif mvrv < 2:
                scores['bull-run'] += 2
            elif mvrv < 6:
                scores['bull-run'] += 1
                scores['euphoria'] += 1
            else:
                scores['euphoria'] += 3
        
        # Pi Cycle
        if pi_cycle:
            scores['euphoria'] += 2
        
        # Puell Multiple
        if pd.notna(puell):
            if puell < 0.5:
                scores['accumulation'] += 2
            elif puell < 2:
                scores['bull-run'] += 2
            elif puell < 4:
                scores['bull-run'] += 1
            else:
                scores['euphoria'] += 2
        
        # Mayer Multiple
        if pd.notna(mayer):
            if mayer < 0.8:
                scores['accumulation'] += 2
            elif mayer < 1.5:
                scores['bull-run'] += 2
            elif mayer < 2.4:
                scores['bull-run'] += 1
            else:
                scores['euphoria'] += 2
        
        # Drawdown
        if drawdown < -70:
            scores['accumulation'] += 3
        elif drawdown < -50:
            scores['bear-market'] += 2
        elif drawdown < -20:
            scores['bull-run'] += 1
        
        # Determinar fase dominante
        dominant_phase = max(scores, key=scores.get)
        confidence = scores[dominant_phase] / max(sum(scores.values()), 1)
        
        phase_names = {
            'accumulation': 'Acumulação - Zona de Compra',
            'bull-run': 'Bull Run - Tendência de Alta',
            'euphoria': 'Euforia - Zona de Risco',
            'bear-market': 'Bear Market - Correção'
        }
        
        return dominant_phase, phase_names[dominant_phase], confidence, scores

def main():
    st.markdown('<h1 class="main-header">₿ Dashboard de Análise de Ciclos do Bitcoin</h1>', 
                unsafe_allow_html=True)
    
    # Inicializar analisador
    analyzer = BitcoinCycleAnalyzer()
    
    # Sidebar com controles
    st.sidebar.header("⚙️ Configurações do Dashboard")
    
    period = st.sidebar.selectbox(
        "📅 Período de Análise",
        ['1y', '2y', '3y', '5y', 'max'],
        index=2,
        help="Selecione o período histórico para análise"
    )
    
    show_halvings = st.sidebar.checkbox("📍 Mostrar Halvings", True)
    show_explanations = st.sidebar.checkbox("📚 Mostrar Explicações", True)
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (60s)", False)
    
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()
    
    # Disclaimer importante
    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Aviso Importante:</strong> Este dashboard combina dados reais (preços) com aproximações 
        dos indicadores on-chain para fins educacionais. Para análises profissionais, recomenda-se 
        usar APIs especializadas como Glassnode ou CoinMetrics.
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('🔄 Carregando dados do Bitcoin...'):
        df = analyzer.fetch_bitcoin_data(period)
        df = analyzer.calculate_technical_indicators(df)
    
    if df is None or df.empty:
        st.error("❌ Não foi possível carregar os dados. Tente novamente mais tarde.")
        return
    
    # Dados atuais
    latest = df.iloc[-1]
    current_price = latest['Close']
    price_change_24h = ((current_price / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0
    
    # Determinar fase atual
    phase_key, phase_name, confidence, phase_scores = analyzer.determine_cycle_phase(latest)
    
    # Header com métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Preço Atual</h3>
            <h2>${current_price:,.0f}</h2>
            <p>USD</p>
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
        next_halving = datetime(2028, 4, 20)  # Estimativa
        days_to_halving = (next_halving - datetime.now()).days
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏰ Próximo Halving</h3>
            <h2>{days_to_halving}</h2>
            <p>dias</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mayer = latest.get('mayer_multiple', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Mayer Multiple</h3>
            <h2>{mayer:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Fase atual do ciclo
    st.markdown(f"""
    <div class="cycle-phase {phase_key}">
        🎯 <strong>FASE ATUAL:</strong> {phase_name}
        <br><small>Confiança: {confidence:.0%} | Baseado em confluência de indicadores</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico principal de preço
    st.subheader("📈 Análise Técnica do Bitcoin")
    
    fig_main = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Preço com Médias Móveis e Pi Cycle', 'Volume de Negociação'),
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2]
    )
    
    # Preço e médias móveis
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name='Preço BTC', 
                  line=dict(color='#F7931A', width=2)),
        row=1, col=1
    )
    
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['MA_111'], name='MA 111d', 
                  line=dict(color='#2196F3', width=1)),
        row=1, col=1
    )
    
    fig_main.add_trace(
        go.Scatter(x=df.index, y=df['MA_350_x2'], name='MA 350d × 2 (Pi Cycle)', 
                  line=dict(color='#F44336', width=1, dash='dot')),
        row=1, col=1
    )
    
    # Volume
    fig_main.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', 
               marker_color='rgba(158,158,158,0.3)'),
        row=2, col=1
    )
    
    # Marcar halvings
    if show_halvings:
        for name, date in analyzer.halving_dates.items():
            if df.index[0] <= date <= df.index[-1]:
                fig_main.add_vline(
                    x=date, line_dash="dash", line_color="purple",
                    annotation_text=name, annotation_position="top"
                )
    
    fig_main.update_layout(
        height=600,
        showlegend=True,
        hovermode='x unified',
        title_text="Análise Técnica Completa do Bitcoin"
    )
    
    fig_main.update_yaxes(type="log", row=1, col=1, title_text="Preço (USD)")
    fig_main.update_yaxes(title_text="Volume", row=2, col=1)
    
    st.plotly_chart(fig_main, use_container_width=True)
    
    # Indicadores de ciclo
    st.subheader("🎯 Indicadores de Ciclo On-Chain")
    
    # Criar subgráficos para indicadores
    fig_indicators = make_subplots(
        rows=4, cols=1,
        subplot_titles=('MVRV Z-Score', 'Puell Multiple', 'RHODL Ratio', 'Reserve Risk'),
        vertical_spacing=0.08
    )
    
    # MVRV Z-Score
    fig_indicators.add_trace(
        go.Scatter(x=df.index, y=df['mvrv_zscore'], name='MVRV Z-Score',
                  line=dict(color='#4CAF50')),
        row=1, col=1
    )
    fig_indicators.add_hline(y=6, line_dash="dash", line_color="red", 
                           annotation_text="Zona de Risco", row=1, col=1)
    fig_indicators.add_hline(y=-0.5, line_dash="dash", line_color="green", 
                           annotation_text="Zona de Oportunidade", row=1, col=1)
    
    # Puell Multiple
    fig_indicators.add_trace(
        go.Scatter(x=df.index, y=df['puell_multiple'], name='Puell Multiple',
                  line=dict(color='#9C27B0')),
        row=2, col=1
    )
    fig_indicators.add_hline(y=4, line_dash="dash", line_color="red", 
                           annotation_text="Topo Histórico", row=2, col=1)
    
    # RHODL Ratio
    fig_indicators.add_trace(
        go.Scatter(x=df.index, y=df['rhodl_ratio'], name='RHODL Ratio',
                  line=dict(color='#FF5722')),
        row=3, col=1
    )
    
    # Reserve Risk
    fig_indicators.add_trace(
        go.Scatter(x=df.index, y=df['reserve_risk'], name='Reserve Risk',
                  line=dict(color='#795548')),
        row=4, col=1
    )
    
    fig_indicators.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig_indicators, use_container_width=True)
    
    # Painel de status dos indicadores
    st.subheader("📊 Status Atual dos Indicadores")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mvrv_current = latest.get('mvrv_zscore', 0)
        if pd.isna(mvrv_current):
            mvrv_status = "N/A"
            mvrv_class = "indicator-warning"
        elif mvrv_current < 0:
            mvrv_status = "OPORTUNIDADE"
            mvrv_class = "indicator-safe"
        elif mvrv_current < 3:
            mvrv_status = "NEUTRO"
            mvrv_class = "indicator-warning"
        else:
            mvrv_status = "RISCO"
            mvrv_class = "indicator-danger"
        
        st.markdown(f"""
        **MVRV Z-Score:** <span class="{mvrv_class}">{mvrv_current:.2f} - {mvrv_status}</span>
        
        - < 0: Zona de oportunidade histórica
        - 0-3: Zona neutra de acumulação
        - 3-6: Zona de atenção
        - > 6: Zona de risco de topo
        """, unsafe_allow_html=True)
    
    with col2:
        pi_current = latest.get('pi_cycle_signal', False)
        pi_status = "🔴 ATIVO" if pi_current else "🟢 INATIVO"
        pi_class = "indicator-danger" if pi_current else "indicator-safe"
        
        st.markdown(f"""
        **Pi Cycle Top:** <span class="{pi_class}">{pi_status}</span>
        
        - Ativo: MA 111 > MA 350 × 2
        - Sinal histórico de topo de ciclo
        - Precisão: ~3 dias do pico real
        """, unsafe_allow_html=True)
    
    with col3:
        puell_current = latest.get('puell_multiple', 1)
        if pd.isna(puell_current):
            puell_status = "N/A"
            puell_class = "indicator-warning"
        elif puell_current < 0.5:
            puell_status = "ACUMULAÇÃO"
            puell_class = "indicator-safe"
        elif puell_current < 4:
            puell_status = "NORMAL"
            puell_class = "indicator-warning"
        else:
            puell_status = "DISTRIBUIÇÃO"
            puell_class = "indicator-danger"
        
        st.markdown(f"""
        **Puell Multiple:** <span class="{puell_class}">{puell_current:.2f} - {puell_status}</span>
        
        - < 0.5: Zona de acumulação
        - 0.5-4: Zona normal
        - > 4: Zona de distribuição
        """, unsafe_allow_html=True)
    
    # Tabela histórica dos ciclos
    if show_explanations:
        st.subheader("📚 Dados Históricos dos Ciclos do Bitcoin")
        
        cycles_data = {
            'Ciclo': ['1º (2009-2012)', '2º (2012-2016)', '3º (2016-2020)', '4º (2020-2024)', 'Atual (2024-?)'],
            'Data do Halving': ['28/11/2012', '09/07/2016', '11/05/2020', '20/04/2024', '~2028'],
            'Preço no Halving': ['$12', '$650', '$8.600', '$64.000', f'${current_price:,.0f}'],
            'Pico Máximo': ['$1.163', '$19.783', '$68.789', 'Em progresso', 'TBD'],
            'Ganho Total': ['9.592%', '3.043%', '800%', 'TBD', 'TBD'],
            'Duração (meses)': ['12', '17', '18', 'TBD', 'TBD'],
            'Correção Máxima': ['-87%', '-84%', '-77%', 'TBD', 'TBD']
        }
        
        df_cycles = pd.DataFrame(cycles_data)
        st.dataframe(df_cycles, use_container_width=True)
    
    # Projeções para o ciclo atual
    st.subheader("🔮 Projeções para o Ciclo Atual (2024-2026)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Cenários de Preço
        
        **🟢 Conservador (30% probabilidade)**
        - **Pico:** $120.000 - $160.000
        - **Timeline:** Q3-Q4 2025
        - **Múltiplo:** 8-10x desde fundo 2022
        
        **🟡 Base (55% probabilidade)**
        - **Pico:** $180.000 - $220.000
        - **Timeline:** Q4 2025 - Q1 2026
        - **Múltiplo:** 12-14x desde fundo 2022
        
        **🟠 Otimista (15% probabilidade)**
        - **Pico:** $250.000 - $350.000
        - **Timeline:** Q2-Q4 2026
        - **Múltiplo:** 16-22x desde fundo 2022
        """)
    
    with col2:
        st.markdown("""
        ### ⚠️ Fatores de Risco
        
        **🔴 Limitantes:**
        - Regulamentação adversa
        - Crise macroeconômica global
        - Reversão de fluxos de ETF
        - Lei dos retornos decrescentes
        
        **🟢 Catalisadores:**
        - Adoção institucional via ETFs
        - Escassez pós-halving
        - Políticas monetárias expansivas
        - Adoção corporativa crescente
        
        **📈 Sinais de Topo a Monitorar:**
        - Pi Cycle Top ativo
        - MVRV Z-Score > 7
        - Puell Multiple > 4
        - Euforia midiática extrema
        """)
    
    # Estratégia recomendada baseada na fase
    st.subheader("💡 Estratégia Recomendada")
    
    strategy_recommendations = {
        'accumulation': {
            'text': """
            🟢 **FASE DE ACUMULAÇÃO - ESTRATÉGIA AGRESSIVA**
            - **DCA:** Implemente Dollar-Cost Averaging semanal/mensal
            - **Compras Extras:** Aproveite quedas >15% para aportes adicionais
            - **Alocação:** Mantenha 80-90% do capital destinado ao Bitcoin
            - **Horizonte:** 18-24 meses até próxima fase
            - **Risco:** Baixo a moderado para horizontes longos
            """,
            'color': '#E8F5E8'
        },
        'bull-run': {
            'text': """
            🟡 **BULL RUN - ESTRATÉGIA DE MANUTENÇÃO**
            - **DCA:** Reduza frequência mas mantenha consistência
            - **Realizações:** Prepare-se para vendas parciais (10-20%)
            - **Monitoramento:** Acompanhe indicadores de topo diariamente
            - **Alocação:** Mantenha posição core mas reduza exposição gradualmente
            - **Risco:** Moderado, volatilidade crescente
            """,
            'color': '#FFF3E0'
        },
        'euphoria': {
            'text': """
            🔴 **EUFORIA - ESTRATÉGIA DE REALIZAÇÃO**
            - **Vendas:** Realize 30-50% das posições imediatamente
            - **Monitoramento:** Acompanhe Pi Cycle Top diariamente
            - **Preparação:** Organize-se para bear market iminente
            - **Posição Final:** Mantenha apenas core de longo prazo (20-30%)
            - **Risco:** Alto, correção iminente
            """,
            'color': '#FFEBEE'
        },
        'bear-market': {
            'text': """
            🔵 **BEAR MARKET - ESTRATÉGIA DE PACIÊNCIA**
            - **Acumulação:** Retome DCA gradualmente
            - **Oportunidades:** Aproveite quedas >20% para compras
            - **Paciência:** Prepare-se para 12-18 meses de lateralização
            - **Educação:** Use o tempo para estudar e se preparar
            - **Risco:** Alto no curto prazo, baixo no longo prazo
            """,
            'color': '#E3F2FD'
        }
    }
    
    current_strategy = strategy_recommendations[phase_key]
    
    st.markdown(f"""
    <div style="background-color: {current_strategy['color']}; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #2196F3;">
        {current_strategy['text']}
    </div>
    """, unsafe_allow_html=True)
    
    # Footer com disclaimers
    st.markdown("---")
    st.markdown("""
    ### ⚠️ Disclaimers Importantes
    
    **Educacional:** Este dashboard é puramente educacional e não constitui consultoria financeira.
    
    **Riscos:** Criptomoedas são investimentos de alto risco com volatilidade extrema.
    
    **DYOR:** Sempre faça sua própria pesquisa antes de tomar decisões de investimento.
    
    **Dados:** Indicadores são aproximações baseadas em dados públicos. Para análises profissionais, use APIs especializadas.
    
    **Responsabilidade:** Invista apenas o que pode perder completamente.
    
    ---
    
    **Última atualização:** """ + datetime.now().strftime("%d/%m/%Y às %H:%M:%S") + """
    
    **Fonte dos dados:** Yahoo Finance (preços) | Indicadores calculados internamente
    """)

if __name__ == "__main__":
    main()
