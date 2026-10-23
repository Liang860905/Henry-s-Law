import streamlit as st
import streamlit.components.v1 as components
import random

# 頁面基本設定
st.set_page_config(page_title="亨利定律互動模擬", layout="wide")

st.title("亨利定律 (Henry's Law) 定量與體積變化模擬")
st.markdown("**核心概念：於定溫、相同難溶性氣體之情況，該難溶性氣體之分壓與溶解度成正比。**")

# ================= 側邊欄：參數控制 =================
st.sidebar.header("⚙️ 實驗參數設定")

mode = st.sidebar.radio(
    "選擇教學情境：",
    [
        "1. 基準狀態 (1P, 1V劑)",
        "2. 壓力變兩倍 (2P, 1V劑)",
        "3. 溶劑體積變兩倍 (1P, 2V劑)",
        "4. 自訂滑桿模式"
    ]
)

if mode == "1. 基準狀態 (1P, 1V劑)":
    P_ratio = 1.0
    V_solv_ratio = 1.0
elif mode == "2. 壓力變兩倍 (2P, 1V劑)":
    P_ratio = 2.0
    V_solv_ratio = 1.0
elif mode == "3. 溶劑體積變兩倍 (1P, 2V劑)":
    P_ratio = 1.0
    V_solv_ratio = 2.0
else:
    P_ratio = st.sidebar.slider("氣體分壓 (P 倍數)", min_value=0.5, max_value=3.0, value=1.0, step=0.5)
    V_solv_ratio = st.sidebar.slider("溶劑體積 (V劑 倍數)", min_value=0.5, max_value=2.5, value=1.0, step=0.5)

st.sidebar.markdown("---")
quiz_mode = st.sidebar.checkbox("🔒 隱藏變化結論（課堂提問模式）", value=False)
show_real_val = st.sidebar.checkbox("📊 顯示 25°C 氧氣真實計算數值", value=False)

# ================= 物理量計算 =================
# 相對倍數計算 (以 1P, 1V劑 為 1.0 倍基準)
s_ratio = P_ratio                         # s = KH * PO2 (僅與分壓成正比)
n_ratio = s_ratio * V_solv_ratio          # n = s * V劑
w_ratio = n_ratio                         # W = n * M
dv_ratio = n_ratio / P_ratio              # ΔV = nRT / P = KH * V劑 * RT (僅與溶劑體積成正比)

# 真實數值參數 (25°C 水中 O2: KH = 1.3e-3 M/atm, R = 0.082, T = 298.15 K, M = 32 g/mol)
KH = 1.3e-3
R_T = 0.08206 * 298.15
M_O2 = 32.0
s_real = KH * P_ratio
n_real = s_real * V_solv_ratio
w_real = n_real * M_O2
dv_real = (n_real * R_T) / P_ratio  # 單位: L

# 產生隨機但固定的粒子座標
def generate_dots(count, x_min, x_max, y_min, y_max, seed_val):
    rng = random.Random(seed_val)
    dots_svg = ""
    for _ in range(int(round(count))):
        cx = rng.uniform(x_min + 8, x_max - 8)
        cy = rng.uniform(y_min + 8, y_max - 8)
        dots_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="#111111" />'
    return dots_svg

# ================= 繪製 SVG 動態示意圖 =================
def render_cylinder_svg(P_mult, V_mult, dV_mult):
    # 容器座標基準
    cyl_bottom = 350
    cyl_width = 180
    
    # 液體高度 (基準 60px)
    h_liq = 60 * V_mult
    y_liq_top = cyl_bottom - h_liq
    
    # 平衡氣相高度 V2 (固定為 100px 以利觀察)
    h_gas_eq = 100
    y_piston_eq = y_liq_top - h_gas_eq
    
    # 活塞下降高度 ΔV (基準 35px)
    h_dv = 35 * dV_mult
    y_piston_init = y_piston_eq - h_dv
    
    # 粒子數量計算 (符合粒子守恆：左圖氣相總數 = 右圖氣相 + 右圖液相)
    dots_liq_eq = int(round(4 * P_mult * V_mult))
    dots_gas_eq = int(round(8 * P_mult))
    dots_gas_init = dots_gas_eq + dots_liq_eq

    # 左圖座標 (x: 60 ~ 240)
    left_gas_dots = generate_dots(dots_gas_init, 60, 240, y_piston_init + 18, y_liq_top, 42)
    # 右圖座標 (x: 380 ~ 560)
    right_gas_dots = generate_dots(dots_gas_eq, 380, 560, y_piston_eq + 18, y_liq_top, 99)
    right_liq_dots = generate_dots(dots_liq_eq, 380, 560, y_liq_top, cyl_bottom, 123)

    p_label = f"{P_mult:g}P atm" if P_mult != 1.0 else "P atm"
    v_label = f"{V_mult:g}V劑" if V_mult != 1.0 else "V劑"

    svg_code = f"""
    <div style="display: flex; justify-content: center; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px;">
    <svg width="650" height="400" viewBox="0 0 650 400" style="font-family: 'Microsoft JhengHei', 'PingFang TC', sans-serif;">
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#000" />
            </marker>
            <marker id="red-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#d9534f" />
            </marker>
        </defs>

        <!-- 標題標示 -->
        <text x="150" y="25" text-anchor="middle" font-size="15" font-weight="bold" fill="#444">剛接觸瞬間（尚未溶解）</text>
        <text x="470" y="25" text-anchor="middle" font-size="15" font-weight="bold" fill="#444">溶解達平衡狀態</text>

        <!-- ================= 左側容器 (未溶解) ================= -->
        <!-- 溶劑區塊 -->
        <rect x="60" y="{y_liq_top}" width="{cyl_width}" height="{h_liq}" fill="#b3d9ff" stroke="#333" stroke-width="1.5" />
        <text x="150" y="{y_liq_top + h_liq/2 + 6}" text-anchor="middle" font-size="16" font-weight="bold" fill="#003366">{v_label}</text>
        
        <!-- 活塞 (V1) -->
        <rect x="60" y="{y_piston_init}" width="{cyl_width}" height="18" fill="#aaaaaa" stroke="#333" stroke-width="2" />
        <!-- 壓力箭頭 -->
        <line x1="150" y1="{y_piston_init - 45}" x2="150" y2="{y_piston_init - 4}" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        <text x="160" y="{y_piston_init - 20}" font-size="15" font-weight="bold">{p_label}</text>

        <!-- 氣相區與標籤 -->
        {left_gas_dots}
        <text x="105" y="{y_piston_init + 45}" font-size="14" font-weight="bold" fill="#222">PO₂={p_label}</text>
        <text x="210" y="{y_liq_top - 15}" font-size="15" font-weight="bold" fill="#222">V₁</text>

        <!-- 容器外壁 -->
        <line x1="60" y1="55" x2="60" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />
        <line x1="240" y1="55" x2="240" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />
        <line x1="60" y1="{cyl_bottom}" x2="240" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />

        <!-- ================= 中間平衡箭頭 ================= -->
        <text x="310" y="200" text-anchor="middle" font-size="15" font-weight="bold">溶解達平衡</text>
        <line x1="260" y1="215" x2="360" y2="215" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />

        <!-- ================= 右側容器 (達平衡) ================= -->
        <!-- 溶劑區塊 -->
        <rect x="380" y="{y_liq_top}" width="{cyl_width}" height="{h_liq}" fill="#b3d9ff" stroke="#333" stroke-width="1.5" />
        <text x="470" y="{y_liq_top + h_liq/2 + 6}" text-anchor="middle" font-size="16" font-weight="bold" fill="#003366">{v_label}</text>

        <!-- 原位置虛線活塞 -->
        <rect x="380" y="{y_piston_init}" width="{cyl_width}" height="18" fill="none" stroke="#666" stroke-width="1.5" stroke-dasharray="4,4" />

        <!-- 平衡位置實線活塞 (V2) -->
        <rect x="380" y="{y_piston_eq}" width="{cyl_width}" height="18" fill="#aaaaaa" stroke="#333" stroke-width="2" />
        <!-- 壓力箭頭 -->
        <line x1="470" y1="{y_piston_eq - 45}" x2="470" y2="{y_piston_eq - 4}" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        <text x="480" y="{y_piston_eq - 20}" font-size="15" font-weight="bold">{p_label}</text>

        <!-- 氣相與液相粒子 -->
        {right_gas_dots}
        {right_liq_dots}
        <text x="425" y="{y_piston_eq + 45}" font-size="14" font-weight="bold" fill="#222">PO₂={p_label}</text>
        <text x="530" y="{y_liq_top - 15}" font-size="15" font-weight="bold" fill="#222">V₂</text>

        <!-- 容器外壁 -->
        <line x1="380" y1="55" x2="380" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />
        <line x1="560" y1="55" x2="560" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />
        <line x1="380" y1="{cyl_bottom}" x2="560" y2="{cyl_bottom}" stroke="#000" stroke-width="2.5" />

        <!-- ΔV 標記雙箭頭 -->
        <line x1="580" y1="{y_piston_init + 9}" x2="580" y2="{y_piston_eq + 9}" stroke="#d9534f" stroke-width="2" marker-start="url(#red-arrow)" marker-end="url(#red-arrow)" />
        <text x="590" y="{(y_piston_init + y_piston_eq)/2 + 14}" font-size="15" font-weight="bold" fill="#d9534f">ΔV</text>
    </svg>
    </div>
    """
    return svg_code

# ================= 版面配置：左圖右公式 =================
col_vis, col_math = st.columns([1.15, 1])

with col_vis:
    components.html(render_cylinder_svg(P_ratio, V_solv_ratio, dv_ratio), height=430)
    st.caption("💡 黑色圓點代表 O₂ 分子。右圖虛線為溶解前活塞高度，實線為達溶解平衡後之活塞高度。")

def format_change_badge(ratio, is_quiz):
    if is_quiz:
        return "👉 變化結果： :orange[**[ 課堂提問遮蔽 ]**]"
    if abs(ratio - 1.0) < 1e-5:
        return "👉 變化結果： :blue[**維持不變 (1.0 倍)**]"
    else:
        return f"👉 變化結果： :red[**變為 {ratio:g} 倍**]"

with col_math:
    st.subheader("📐 定量公式推導與變化關係")

    # 公式 1: 溶解氣體體積 ΔV
    with st.container(border=True):
        st.markdown("**1. 溶解氣體體積 ($\\Delta V = V_1 - V_2$)**")
        st.latex(r"P_{\text{O}_2} \Delta V = n_{\text{O}_2} R T \implies \Delta V = K_{\text{H}} \times V_{\text{劑}} \times R T")
        st.markdown(format_change_badge(dv_ratio, quiz_mode))
        if show_real_val and not quiz_mode:
            st.caption(f"25°C 真實計算值：ΔV = {dv_real*1000:.2f} mL (固定正比於溶劑體積，與分壓無關)")

    # 公式 2: 氣體溶解度 s
    with st.container(border=True):
        st.markdown("**2. 此時水中 $C_{M(\text{O}_2)}$ 即為 $\\text{O}_2$ 之溶解度 ($s$)**")
        st.latex(r"s = K_{\text{H}} \times P_{\text{O}_2}")
        st.markdown(format_change_badge(s_ratio, quiz_mode))
        if show_real_val and not quiz_mode:
            st.caption(f"25°C 真實計算值：s = {s_real:.4e} M")

    # 公式 3: 溶解氣體莫耳數 n
    with st.container(border=True):
        st.markdown("**3. 溶解氣體莫耳數 ($n_{\\text{O}_2}$)**")
        st.latex(r"n_{\text{O}_2} = s \times V_{\text{劑}} = K_{\text{H}} \times P_{\text{O}_2} \times V_{\text{劑}}")
        st.markdown(format_change_badge(n_ratio, quiz_mode))
        if show_real_val and not quiz_mode:
            st.caption(f"25°C 真實計算值：n = {n_real:.4e} mol")

    # 公式 4: 溶解氣體質量 W
    with st.container(border=True):
        st.markdown("**4. 溶解氣體質量 ($W_{\\text{O}_2}$)**")
        st.latex(r"W_{\text{O}_2} = n_{\text{O}_2} \times M_{\text{O}_2} = K_{\text{H}} \times P_{\text{O}_2} \times V_{\text{劑}} \times M_{\text{O}_2}")
        st.markdown(format_change_badge(w_ratio, quiz_mode))
        if show_real_val and not quiz_mode:
            st.caption(f"25°C 真實計算值：W = {w_real*1000:.3f} mg")
