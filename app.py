import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. 參數設定區
# ==========================================
SUNGSHU_CAPITAL = 4000000
ALLEN_CAPITAL = 4000000
TOTAL_PRINCIPAL = 8000000
RESERVE_CAPITAL = 1600000
# ==========================================

st.set_page_config(page_title="量化交易總覽", layout="wide", initial_sidebar_state="collapsed")

# 引入 FontAwesome 與自訂全局 CSS
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .stApp {
            background-color: #f7fafc;
            font-family: 'Helvetica Neue', Helvetica, Arial, 'Microsoft JhengHei', sans-serif;
        }
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    dates = ['202104-202110', '202111-202207', '202208-202302', '202401-202412', '202504-202601', '202602-202609']
    df = pd.DataFrame({
        'Date': dates,
        'LS_Realized_Cum': [169845, -219812, -313818, 540000, 895409, 1154236],
        'LS_Unrealized': [0, 0, 0, 0, 0, -429631], 
        'Future_Realized_Cum': [0, 127469, 334800, 750000, 1200000, 1414718],
        'Future_Unrealized': [0, 0, 0, 0, 0, -564853],
        'AI_Realized_Cum': [490831, -359488, -1089156, -1378017, -1378017, -1378017],
        'AI_Unrealized': [0, 0, 0, 0, 0, 0],
        'Bond_Realized_Cum': [0, 80299, 199160, -312672, -312672, -312672],
        'Bond_Unrealized': [0, 0, 0, 0, 0, 0]
    })
    return df

df = load_data()
latest = df.iloc[-1]

# 運算邏輯 (總部位本金不再加回備用資金)
total_realized = latest['LS_Realized_Cum'] + latest['Future_Realized_Cum']
total_unrealized = latest['LS_Unrealized'] + latest['Future_Unrealized'] + latest['AI_Unrealized'] + latest['Bond_Unrealized']
total_asset = TOTAL_PRINCIPAL + total_realized + total_unrealized

# 策略狀態設定
strats = {
    'LS': {'name': 'Long-Short', 'color': '#3182ce', 'status': '線上', 'real': latest['LS_Realized_Cum'], 'unreal': latest['LS_Unrealized']},
    'Future': {'name': '期貨個股對鎖', 'color': '#38a169', 'status': '線上', 'real': latest['Future_Realized_Cum'], 'unreal': latest['Future_Unrealized']},
    'AI': {'name': 'AI auto trade', 'color': '#805ad5', 'status': '已下線', 'real': latest['AI_Realized_Cum'], 'unreal': latest['AI_Unrealized']},
    'Bond': {'name': '債券', 'color': '#dd6b20', 'status': '已下線', 'real': latest['Bond_Realized_Cum'], 'unreal': latest['Bond_Unrealized']}
}

# ==========================================
# UI 區塊 1: 頂部 Header
# ==========================================
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 30px;">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="background-color: #2b3a55; color: white; width: 40px; height: 40px; border-radius: 8px; display: flex; justify-content: center; align-items: center; font-size: 18px;">
            <i class="fas fa-chart-line"></i>
        </div>
        <div>
            <div style="font-size: 20px; font-weight: bold; color: #1a202c;">量化交易總覽</div>
            <div style="font-size: 14px; color: #718096;">SungShu × Allen</div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 12px; color: #718096;">投資紀錄</div>
        <div style="font-size: 16px; font-weight: bold; color: #1a202c;">TWD 新臺幣</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div>
        <div style="font-size: 12px; font-weight: bold; color: #a0aec0; letter-spacing: 1px;">PORTFOLIO OVERVIEW</div>
        <div style="font-size: 24px; font-weight: bold; color: #2d3748; margin-top: 5px;"></div>
    </div>
    <div style="text-align: right; color: #718096; font-size: 14px;">資料截至<br><span style="color: #2d3748; font-weight: bold;">最新日期</span></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# UI 區塊 2: 核心數據卡片 (4:6 比例)
# ==========================================
col_l, col_r = st.columns([4, 6])

with col_l:
    # 總部位深色卡片
    st.markdown(f"""
    <div style="background-color: #1a2a40; color: white; border-radius: 12px; padding: 25px; height: 260px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div>
            <div style="font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 8px;">
                <i class="far fa-file-alt"></i> 總部位本金
            </div>
            <div style="font-size: 13px; color: #a0aec0; margin-top: 4px;">(已含未實現損益)</div>
            <div style="font-size: 16px; color: #e2e8f0; margin-top: 25px;">NT$</div>
            <div style="font-size: 42px; font-weight: bold;">{total_asset:,.0f}</div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #a0aec0; border-top: 1px solid #2d3748; padding-top: 15px;">
            <span>不包含備用資金</span>
            <span>目前部位價值</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_r:
    # 右側 4 個白色指標卡片
    def white_card(title, value, sub_text):
        return f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; height: 120px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
            <div style="font-size: 14px; font-weight: bold; color: #718096;">{title}</div>
            <div style="font-size: 24px; font-weight: bold; color: #2d3748;">{value}</div>
            <div style="font-size: 12px; color: #a0aec0;">{sub_text}</div>
        </div>
        """
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(white_card("累積已實現損益", f"${total_realized:,.0f}", "本期2026/02至今累積合計"), unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(white_card("備用資金", f"${RESERVE_CAPITAL:,.0f}", "預留期貨保證金部位，防止國際黑天鵝事件"), unsafe_allow_html=True)
    with r_col2:
        u_color = "#e53e3e" if total_unrealized < 0 else "#38a169"
        u_value = f"<span style='color: {u_color};'>${total_unrealized:,.0f}</span>"
        st.markdown(white_card("未實現損益", u_value, "各策略明細見下方"), unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(white_card("總投資本金", f"${TOTAL_PRINCIPAL:,.0f}", "總投入本金"), unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ==========================================
# UI 區塊 3: 部位分配 Bar
# ==========================================
st.markdown(f"""
<div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px 25px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
    <div style="font-weight: bold; color: #718096; font-size: 15px;"><i class="fas fa-layer-group"></i> 部位分配</div>
    <div style="display: flex; gap: 60px;">
        <div style="display: flex; align-items: center;"><span style="background: #e6f2ff; color: #3182ce; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; border-radius: 50%; font-size: 12px; margin-right: 10px; font-weight: bold;">S</span> <span style="color:#4a5568; margin-right: 15px;">SungShu</span> <span style="font-weight: bold; font-size: 20px; color: #1a202c;">NT$ {SUNGSHU_CAPITAL:,.0f}</span></div>
        <div style="display: flex; align-items: center;"><span style="background: #e6ffed; color: #38a169; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; border-radius: 50%; font-size: 12px; margin-right: 10px; font-weight: bold;">A</span> <span style="color:#4a5568; margin-right: 15px;">Allen</span> <span style="font-weight: bold; font-size: 20px; color: #1a202c;">NT$ {ALLEN_CAPITAL:,.0f}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# ==========================================
# UI 區塊 4: 策略損益圖表
# ==========================================
st.markdown("""
<div style="font-size: 12px; font-weight: bold; color: #a0aec0; letter-spacing: 1px;">STRATEGY PERFORMANCE</div>
<div style="font-size: 20px; font-weight: bold; color: #2d3748; margin-top: 5px;">策略累積損益</div>
<div style="font-size: 13px; color: #718096; margin-bottom: 15px;">2021年起 • 每月紀錄 • 單位：新臺幣</div>
""", unsafe_allow_html=True)

fig = go.Figure()

for prefix, info in zip(['LS', 'Future', 'AI', 'Bond'], [strats['LS'], strats['Future'], strats['AI'], strats['Bond']]):
    name = info['name']
    color = info['color']
    
    # 實線
    fig.add_trace(go.Scatter(x=df['Date'], y=df[f'{prefix}_Realized_Cum'], mode='lines+markers', name=f'{name} (已實現)', line=dict(color=color, width=2, dash='solid')))
    
    # 虛線
    if df[f'{prefix}_Unrealized'].sum() != 0:
        total_pnl = df[f'{prefix}_Realized_Cum'] + df[f'{prefix}_Unrealized']
        fig.add_trace(go.Scatter(x=df['Date'], y=total_pnl, mode='lines+markers', name=f'{name} (含未實現)', line=dict(color=color, width=2, dash='dash')))

fig.update_layout(
    height=450,
    plot_bgcolor='white',
    paper_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    xaxis=dict(showgrid=True, gridcolor='#edf2f7', linecolor='#e2e8f0'),
    yaxis=dict(showgrid=True, gridcolor='#edf2f7', linecolor='#e2e8f0', zeroline=True, zerolinecolor='#cbd5e0'),
    margin=dict(l=0, r=0, t=20, b=0)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# ==========================================
# UI 區塊 5: 底部各策略卡片 (分線上/已下線)
# ==========================================
def strat_card(info):
    badge_bg = "#e6ffed" if info['status'] == "線上" else "#edf2f7"
    badge_color = "#38a169" if info['status'] == "線上" else "#a0aec0"
    u_color = "#e53e3e" if info['unreal'] < 0 else ("#38a169" if info['unreal'] > 0 else "#2d3748")
    
    return f"""
    <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <div style="font-weight: bold; font-size: 18px; color: #1a202c;">
                <span style="color: {info['color']}; margin-right: 8px;">●</span>{info['name']}
            </div>
            <div style="background-color: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;">{info['status']}</div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 25px;">
            <div>
                <div style="font-size: 13px; color: #718096; margin-bottom: 5px;">累積已實現</div>
                <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{info['real']:,.0f}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #718096; margin-bottom: 5px;">未實現損益</div>
                <div style="font-size: 20px; font-weight: bold; color: {u_color};">{info['unreal']:,.0f}</div>
            </div>
        </div>
        <div style="border-top: 1px solid #edf2f7; padding-top: 15px; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 13px; color: #a0aec0;">含未實現合計</div>
            <div style="font-weight: bold; font-size: 16px; color: #4a5568;">{(info['real'] + info['unreal']):,.0f}</div>
        </div>
    </div>
    """

col_s1, col_s2 = st.columns(2)

with col_s1:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px;">
        <div style="font-size: 18px; font-weight: bold; color: #2d3748;">線上策略</div>
        <div style="font-size: 12px; color: #a0aec0;">持續運行</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(strat_card(strats['LS']), unsafe_allow_html=True)
    st.markdown(strat_card(strats['Future']), unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px;">
        <div style="font-size: 18px; font-weight: bold; color: #2d3748;">已下線策略</div>
        <div style="font-size: 12px; color: #a0aec0;">保留歷史紀錄</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(strat_card(strats['AI']), unsafe_allow_html=True)
    st.markdown(strat_card(strats['Bond']), unsafe_allow_html=True)