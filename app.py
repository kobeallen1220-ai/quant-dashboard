# -*- coding: utf-8 -*-
"""量化交易總覽(Streamlit 手機版) v1.1(2026-11-03 搬到 Oracle_Agent/97_tools/capital_site_v1_0/streamlit_app)。
資料不再寫死：直接讀 chatgpt.site 網站的公開 API(publish_capital_v1_0.py 發布的同一份資料)，
所以之後更新數字只要發布一次，兩個網站都會更新；API 讀不到時改用同資料夾 data_fallback.json。"""
import json
import urllib.request
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

API_URL = "https://allen-sungshu-capital.kobeallen1220.chatgpt.site/api/portfolio"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Capital-Viewer/1.0"
ONLINE = ("longShort", "futuresHedge")  # 線上策略；已下線策略的虧損不計入總部位與累積已實現(Allen 2026-11-03)


@st.cache_data(ttl=300)
def fetch_portfolio():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": UA})
        return json.load(urllib.request.urlopen(req, timeout=15))["data"], "網站"
    except Exception:
        return json.loads((Path(__file__).parent / "data_fallback.json").read_text(encoding="utf-8")), "備援檔"


P, SOURCE = fetch_portfolio()
CAP = P["capital"]
SUNGSHU_CAPITAL = CAP["sungShu"] or 0
ALLEN_CAPITAL = CAP["allen"] or 0
TOTAL_PRINCIPAL = CAP["investedPrincipal"] or 0
RESERVE_CAPITAL = CAP["reserve"] or 0
AS_OF = P["asOf"].replace("-", "/")
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

def load_data():
    keys = {"LS": "longShort", "Future": "futuresHedge", "AI": "aiAutoTrade", "Bond": "bonds"}
    rows = [m for m in P["monthly"] if any(m[k]["realized"] is not None for k in keys.values())]
    return pd.DataFrame([{"Date": m["month"],
                          **{f"{p}_Realized_Cum": m[k]["realized"] or 0 for p, k in keys.items()},
                          **{f"{p}_Unrealized": m[k]["unrealized"] or 0 for p, k in keys.items()}} for m in rows])

df = load_data()
latest = df.iloc[-1]

# 運算邏輯：總部位直接用發布資料的 positionEquity(不含備用資金)；累積已實現只算線上策略
total_realized = latest['LS_Realized_Cum'] + latest['Future_Realized_Cum']
total_unrealized = latest['LS_Unrealized'] + latest['Future_Unrealized'] + latest['AI_Unrealized'] + latest['Bond_Unrealized']
total_asset = CAP["positionEquity"] if CAP["positionEquity"] is not None else TOTAL_PRINCIPAL + total_realized + total_unrealized

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
    <div style="text-align: right; color: #718096; font-size: 14px;">資料截至<br><span style="color: #2d3748; font-weight: bold;">{AS_OF}</span></div>
</div>
""".replace("{AS_OF}", AS_OF), unsafe_allow_html=True)

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
            <span>不含備用資金</span>
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
        st.markdown(white_card("累積已實現損益", f"${total_realized:,.0f}", "線上策略累積合計（不含已下線策略）"), unsafe_allow_html=True)
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
# UI 區塊 2b: 總部位較前次更新(2026-11-03 Allen：「新增一個欄位，對比前一次更新的資料，總部位損益是增減了多少」)
# 前次＝上一筆有資料的月份，用同一公式(本金＋線上已實現＋線上未實現)計算
# ==========================================
if len(df) >= 2:
    def _eq(r):
        return TOTAL_PRINCIPAL + r['LS_Realized_Cum'] + r['Future_Realized_Cum'] + r['LS_Unrealized'] + r['Future_Unrealized']
    prev_eq = _eq(df.iloc[-2])
    diff = total_asset - prev_eq
    d_color = "#e53e3e" if diff < 0 else ("#38a169" if diff > 0 else "#2d3748")
    prev_month = df['Date'].iloc[-2].replace('-', '/')
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px 25px; display: flex; flex-wrap: wrap; gap: 6px 20px; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05); margin-bottom: 20px;">
        <div>
            <div style="font-size: 14px; font-weight: bold; color: #718096;"><i class="fas fa-arrow-right-arrow-left"></i> 總部位較前次更新</div>
            <div style="font-size: 12px; color: #a0aec0;">前次 {prev_month}：{prev_eq:,.0f} → 本次 {AS_OF}：{total_asset:,.0f}</div>
        </div>
        <div style="font-size: 24px; font-weight: bold; color: {d_color};">{diff:+,.0f}<span style="font-size: 14px; margin-left: 6px;">（{diff / prev_eq:+.2%}）</span></div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# UI 區塊 3: 部位分配 Bar
# ==========================================
st.markdown(f"""
<div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px 25px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
    <div style="font-weight: bold; color: #718096; font-size: 15px;"><i class="fas fa-layer-group"></i> 部位分配</div>
    <div style="display: flex; flex-wrap: wrap; gap: 8px 40px;">
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

# 2026-11-03 手機版修正：原本圖例擠在圖上方、8 條線(含整條與實線重疊的虛線)＋「x unified」提示框會蓋滿手機畫面。
# 改為：X 軸用期末月份(兩行「2021／10月」)，提示顯示完整期間；Y 軸以「萬元」顯示；圖例移到圖下方；
# 未實現只畫「最後一段」虛線(前一期→本期含未實現)，不再畫整條重疊虛線；關閉縮放與工具列避免手機誤觸。
x_label = [d[:4] + '<br>' + d[5:] + '月' for d in df['Date']]  # 兩行，手機上不重疊
# 提示顯示該期間(上一筆資料的下個月～本月)
_prev = [None] + list(df['Date'][:-1])
df['Date'] = [d.replace('-', '/') if p is None else
              f"{(pd.Period(p, 'M') + 1).strftime('%Y/%m')}～{d.replace('-', '/')}" for p, d in zip(_prev, df['Date'])]
fig = go.Figure()

for prefix, info in zip(['LS', 'Future', 'AI', 'Bond'], [strats['LS'], strats['Future'], strats['AI'], strats['Bond']]):
    name = info['name']
    color = info['color']
    real = df[f'{prefix}_Realized_Cum']
    fig.add_trace(go.Scatter(
        x=x_label, y=real / 10000, mode='lines+markers', name=name, legendgroup=prefix,
        line=dict(color=color, width=2.5), marker=dict(size=6), customdata=list(zip(df['Date'], real)),
        hovertemplate=f'{name}｜%{{customdata[0]}}<br>累積已實現 %{{customdata[1]:,.0f}}<extra></extra>'))
    unreal = df[f'{prefix}_Unrealized'].iloc[-1]
    if unreal != 0:
        total = real.iloc[-1] + unreal
        fig.add_trace(go.Scatter(
            x=x_label[-2:], y=[real.iloc[-2] / 10000, total / 10000], mode='lines+markers', name=f'{name}（含未實現）',
            legendgroup=prefix, showlegend=False, line=dict(color=color, width=2, dash='dot'),
            marker=dict(size=[0, 8], symbol='circle-open'),
            hovertemplate=f'{name}｜含未實現 {total:,.0f}<br>（未實現 {unreal:,.0f}）<extra></extra>'))

fig.update_layout(
    height=380,
    plot_bgcolor='white',
    paper_bgcolor='rgba(0,0,0,0)',
    hovermode="closest",
    dragmode=False,
    font=dict(size=12),
    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=12)),
    xaxis=dict(showgrid=False, linecolor='#e2e8f0', fixedrange=True, tickangle=0),
    yaxis=dict(title=dict(text='萬元', font=dict(size=11)), showgrid=True, gridcolor='#edf2f7', zeroline=True,
               zerolinecolor='#94a3b8', fixedrange=True, tickformat=',.0f'),
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})
st.markdown("<div style='font-size: 12px; color: #a0aec0;'>實線＝累積已實現；點線＋空心圈＝最新一期含未實現。點一下線上的點可看金額。"
            f"X 軸為各期間期末月份。資料來源：{SOURCE}。</div>", unsafe_allow_html=True)

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