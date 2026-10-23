
import streamlit as st
import streamlit.components.v1 as components

# 頁面設定
st.set_page_config(page_title="亨利定律互動模擬", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("### 亨利定律整理：於定溫、相同難溶性氣體之情況，該難溶性氣體之分壓與溶解度成正比")

# ================= 頂部控制面板 =================
with st.container(border=True):
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.5, 1.5, 1.2, 1.2])

    if "p_val" not in st.session_state:
        st.session_state.p_val = 2.0
    if "v_val" not in st.session_state:
        st.session_state.v_val = 1.0

    with ctrl_col3:
        st.markdown("**⚡ 快速套用課本情境**")
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        if btn_c1.button("1P, 1V", use_container_width=True):
            st.session_state.p_val = 1.0
            st.session_state.v_val = 1.0
        if btn_c2.button("2P, 1V", use_container_width=True):
            st.session_state.p_val = 2.0
            st.session_state.v_val = 1.0
        if btn_c3.button("1P, 2V", use_container_width=True):
            st.session_state.p_val = 1.0
            st.session_state.v_val = 2.0

    with ctrl_col1:
        P_ratio = st.slider(
            "🔹 連續調整【實驗組】氣體分壓 (P 倍數)",
            min_value=0.5, max_value=3.0, step=0.1, key="p_val"
        )

    with ctrl_col2:
        V_solv_ratio = st.slider(
            "💧 連續調整【實驗組】溶劑體積 (V劑 倍數)",
            min_value=0.5, max_value=2.5, step=0.1, key="v_val"
        )

    with ctrl_col4:
        st.markdown("**🛠️ 教學輔助設定**")
        quiz_mode = st.checkbox("🔒 遮蔽變化結論 (提問模式)", value=False)
        anim_speed = st.slider(
            "粒子移動速度", min_value=0.0, max_value=3.0,
            value=1.2, step=0.2, label_visibility="collapsed"
        )

# ================= 物理量倍數計算 =================
s_ratio = P_ratio
n_ratio = s_ratio * V_solv_ratio
w_ratio = n_ratio
dv_ratio = n_ratio / P_ratio

# ================= 動態粒子與並列容器 Canvas 渲染 =================
def render_dual_canvas(P_exp, V_exp, dV_exp, speed):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; font-family: 'Microsoft JhengHei', 'PingFang TC', sans-serif; }}
        #canvas-wrap {{
            width: 100%;
            background: #ffffff;
            border: 2px solid #dcdcdc;
            border-radius: 12px;
            box-sizing: border-box;
            overflow: hidden;
        }}
        canvas {{ width: 100%; height: auto; display: block; }}
    </style>
    </head>
    <body>
    <div id="canvas-wrap">
        <canvas id="simCanvas"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('simCanvas');
        const ctx = canvas.getContext('2d');

        const LOGICAL_W = 1400;
        const LOGICAL_H = 540;
        const dpr = window.devicePixelRatio || 1;
        canvas.width = LOGICAL_W * dpr;
        canvas.height = LOGICAL_H * dpr;
        ctx.scale(dpr, dpr);

        const P_EXP = {P_exp};
        const V_EXP = {V_exp};
        const DV_EXP = {dV_exp};
        const SPEED = {speed};

        const CYL_BOTTOM = 495;
        const CYL_TOP = 75;
        const CYL_W = 200;
        const PISTON_H = 18;
        const BASE_LIQ_H = 65;
        const GAS_EQ_H = 115;
        const BASE_DV_H = 48;

        function createParticles(count, xMin, xMax, yMin, yMax, isLiquid) {{
            const arr = [];
            const r = 5;
            const spdMult = isLiquid ? 0.55 : 1.0;

            for (let i = 0; i < count; i++) {{
                const angle = Math.random() * Math.PI * 2;
                const v = (1.2 + Math.random() * 1.0) * spdMult;

                arr.push({{
                    x: xMin + r + 2 + Math.random() * Math.max(1, (xMax - xMin - 2 * r - 4)),
                    y: yMin + r + 2 + Math.random() * Math.max(1, (yMax - yMin - 2 * r - 4)),
                    vx: Math.cos(angle) * v,
                    vy: Math.sin(angle) * v,
                    r: r,
                    xMin: xMin, xMax: xMax,
                    yMin: yMin, yMax: yMax
                }});
            }}
            return arr;
        }}

        function buildGroup(offsetX, pMult, vMult, dvMult, titleText, themeColor) {{
            const hLiq = BASE_LIQ_H * vMult;
            const yLiqTop = CYL_BOTTOM - hLiq;
            const yPistonEq = yLiqTop - GAS_EQ_H;
            const hDv = BASE_DV_H * dvMult;
            const yPistonInit = yPistonEq - hDv;

            const x1 = offsetX + 55;
            const x2 = offsetX + 385;

            const nLiqEq = Math.max(1, Math.round(5 * pMult * vMult));
            const nGasEq = Math.max(1, Math.round(10 * pMult));
            const nGasInit = nGasEq + nLiqEq;

            const pInitGas = createParticles(nGasInit, x1, x1 + CYL_W, yPistonInit + PISTON_H, yLiqTop, false);
            const pEqGas = createParticles(nGasEq, x2, x2 + CYL_W, yPistonEq + PISTON_H, yLiqTop, false);
            const pEqLiq = createParticles(nLiqEq, x2, x2 + CYL_W, yLiqTop, CYL_BOTTOM, true);

            return {{
                offsetX, titleText, themeColor,
                pMult, vMult, dvMult,
                x1, x2, hLiq, yLiqTop, yPistonEq, hDv, yPistonInit,
                pInitGas, pEqGas, pEqLiq
            }};
        }}

        const baseGroup = buildGroup(15, 1.0, 1.0, 1.0, "【基準對照組】 1.0 P atm 、 1.0 V劑", "#2b579a");
        const expGroup = buildGroup(715, P_EXP, V_EXP, DV_EXP, `【實驗調整組】 ${{P_EXP.toFixed(1)}} P atm 、 ${{V_EXP.toFixed(1)}} V劑`, "#b02a37");

        function drawArrow(x1, y1, x2, y2, color="#000", lineWidth=2.2) {{
            const headlen = 9;
            const dx = x2 - x1;
            const dy = y2 - y1;
            const angle = Math.atan2(dy, dx);

            ctx.strokeStyle = color;
            ctx.fillStyle = color;
            ctx.lineWidth = lineWidth;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(x2, y2);
            ctx.lineTo(x2 - headlen * Math.cos(angle - Math.PI / 6), y2 - headlen * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(x2 - headlen * Math.cos(angle + Math.PI / 6), y2 - headlen * Math.sin(angle + Math.PI / 6));
            ctx.closePath();
            ctx.fill();
        }}

        function drawDoubleArrow(x, y1, y2, color="#d9534f") {{
            drawArrow(x, (y1 + y2) / 2, x, y1, color, 2);
            drawArrow(x, (y1 + y2) / 2, x, y2, color, 2);
        }}

        function updateAndDrawParticles(particles) {{
            ctx.fillStyle = "#111111";

            for (let p of particles) {{
                p.x += p.vx * SPEED;
                p.y += p.vy * SPEED;

                if (p.x - p.r < p.xMin + 2) {{ p.x = p.xMin + p.r + 2; p.vx *= -1; }}
                if (p.x + p.r > p.xMax - 2) {{ p.x = p.xMax - p.r - 2; p.vx *= -1; }}
                if (p.y - p.r < p.yMin + 2) {{ p.y = p.yMin + p.r + 2; p.vy *= -1; }}
                if (p.y + p.r > p.yMax - 2) {{ p.y = p.yMax - p.r - 2; p.vy *= -1; }}

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fill();
            }}
        }}

        function drawGroup(g) {{
            const pText = g.pMult === 1.0 ? "P atm" : `${{Number(g.pMult.toFixed(1))}}P atm`;
            const vText = g.vMult === 1.0 ? "V劑" : `${{Number(g.vMult.toFixed(1))}}V劑`;

            ctx.fillStyle = g.themeColor;
            ctx.font = "bold 20px 'Microsoft JhengHei', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(g.titleText, g.offsetX + 335, 32);

            ctx.fillStyle = "#555";
            ctx.font = "bold 15px 'Microsoft JhengHei', sans-serif";
            ctx.fillText("剛接觸瞬間 (未溶解)", g.x1 + CYL_W / 2, 60);
            ctx.fillText("溶解達平衡狀態", g.x2 + CYL_W / 2, 60);

            // 左容器：溶劑與初始活塞
            ctx.fillStyle = "#b8daff";
            ctx.strokeStyle = "#333";
            ctx.lineWidth = 1.5;
            ctx.fillRect(g.x1, g.yLiqTop, CYL_W, g.hLiq);
            ctx.strokeRect(g.x1, g.yLiqTop, CYL_W, g.hLiq);

            ctx.fillStyle = "#003366";
            ctx.font = "bold 18px 'Microsoft JhengHei', sans-serif";
            ctx.fillText(vText, g.x1 + CYL_W / 2, g.yLiqTop + g.hLiq / 2 + 7);

            ctx.fillStyle = "#a6a6a6";
            ctx.strokeStyle = "#222";
            ctx.lineWidth = 2;
            ctx.fillRect(g.x1, g.yPistonInit, CYL_W, PISTON_H);
            ctx.strokeRect(g.x1, g.yPistonInit, CYL_W, PISTON_H);

            drawArrow(g.x1 + CYL_W / 2, g.yPistonInit - 45, g.x1 + CYL_W / 2, g.yPistonInit - 2, "#000", 2.2);

            ctx.fillStyle = "#000";
            ctx.textAlign = "left";
            ctx.font = "bold 16px 'Microsoft JhengHei', sans-serif";
            ctx.fillText(pText, g.x1 + CYL_W / 2 + 8, g.yPistonInit - 18);

            updateAndDrawParticles(g.pInitGas);

            ctx.fillStyle = "#111";
            ctx.font = "bold 16px 'Microsoft JhengHei', sans-serif";
            ctx.textAlign = "left";
            ctx.fillText(`PO₂=${{pText}}`, g.x1 + 12, g.yPistonInit + 42);
            ctx.textAlign = "right";
            ctx.fillText("V₁", g.x1 + CYL_W - 12, g.yLiqTop - 12);

            ctx.strokeStyle = "#000";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(g.x1, CYL_TOP);
            ctx.lineTo(g.x1, CYL_BOTTOM);
            ctx.lineTo(g.x1 + CYL_W, CYL_BOTTOM);
            ctx.lineTo(g.x1 + CYL_W, CYL_TOP);
            ctx.stroke();

            // 中間過渡箭頭
            ctx.fillStyle = "#000";
            ctx.textAlign = "center";
            ctx.font = "bold 16px 'Microsoft JhengHei', sans-serif";
            ctx.fillText("溶解達平衡", g.x1 + CYL_W + 65, 290);
            drawArrow(g.x1 + CYL_W + 15, 305, g.x2 - 15, 305, "#000", 2.5);

            // 右容器：平衡狀態
            ctx.fillStyle = "#b8daff";
            ctx.strokeStyle = "#333";
            ctx.lineWidth = 1.5;
            ctx.fillRect(g.x2, g.yLiqTop, CYL_W, g.hLiq);
            ctx.strokeRect(g.x2, g.yLiqTop, CYL_W, g.hLiq);

            // 原活塞位置虛線
            ctx.save();
            ctx.setLineDash([5, 5]);
            ctx.strokeStyle = "#666";
            ctx.lineWidth = 1.8;
            ctx.strokeRect(g.x2, g.yPistonInit, CYL_W, PISTON_H);
            ctx.restore();

            // 平衡活塞
            ctx.fillStyle = "#a6a6a6";
            ctx.strokeStyle = "#222";
            ctx.lineWidth = 2;
            ctx.fillRect(g.x2, g.yPistonEq, CYL_W, PISTON_H);
            ctx.strokeRect(g.x2, g.yPistonEq, CYL_W, PISTON_H);

            drawArrow(g.x2 + CYL_W / 2, g.yPistonEq - 45, g.x2 + CYL_W / 2, g.yPistonEq - 2, "#000", 2.2);

            ctx.fillStyle = "#000";
            ctx.textAlign = "left";
            ctx.font = "bold 16px 'Microsoft JhengHei', sans-serif";
            ctx.fillText(pText, g.x2 + CYL_W / 2 + 8, g.yPistonEq - 18);

            updateAndDrawParticles(g.pEqGas);
            updateAndDrawParticles(g.pEqLiq);

            ctx.fillStyle = "#003366";
            ctx.textAlign = "center";
            ctx.font = "bold 18px 'Microsoft JhengHei', sans-serif";
            ctx.fillText(vText, g.x2 + CYL_W / 2, g.yLiqTop + g.hLiq / 2 + 7);

            ctx.fillStyle = "#111";
            ctx.font = "bold 16px 'Microsoft JhengHei', sans-serif";
            ctx.textAlign = "left";
            ctx.fillText(`PO₂=${{pText}}`, g.x2 + 12, g.yPistonEq + 42);
            ctx.textAlign = "right";
            ctx.fillText("V₂", g.x2 + CYL_W - 12, g.yLiqTop - 12);

            ctx.strokeStyle = "#000";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(g.x2, CYL_TOP);
            ctx.lineTo(g.x2, CYL_BOTTOM);
            ctx.lineTo(g.x2 + CYL_W, CYL_BOTTOM);
            ctx.lineTo(g.x2 + CYL_W, CYL_TOP);
            ctx.stroke();

            // ΔV 紅色雙向箭頭
            const dvX = g.x2 + CYL_W + 22;
            drawDoubleArrow(dvX, g.yPistonInit + PISTON_H / 2, g.yPistonEq + PISTON_H / 2, "#d9534f");

            ctx.fillStyle = "#d9534f";
            ctx.textAlign = "left";
            ctx.font = "bold 17px 'Microsoft JhengHei', sans-serif";
            ctx.fillText("ΔV", dvX + 8, (g.yPistonInit + g.yPistonEq + PISTON_H) / 2 + 6);
        }}

        function animate() {{
            ctx.clearRect(0, 0, LOGICAL_W, LOGICAL_H);

            ctx.save();
            ctx.strokeStyle = "#cccccc";
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 6]);
            ctx.beginPath();
            ctx.moveTo(700, 15);
            ctx.lineTo(700, LOGICAL_H - 15);
            ctx.stroke();
            ctx.restore();

            drawGroup(baseGroup);
            drawGroup(expGroup);

            requestAnimationFrame(animate);
        }}

        animate();
    </script>
    </body>
    </html>
    """
    return html_code


components.html(
    render_dual_canvas(P_ratio, V_solv_ratio, dv_ratio, anim_speed),
    height=555,
    scrolling=False
)

# ================= 下方公式區 =================
def badge_text(mult, is_quiz):
    if is_quiz:
        return ":orange[**[ 課堂提問遮蔽 ]**]"
    if abs(mult - 1.0) < 1e-4:
        return ":blue[**不變 (1.0 倍)**]"
    return f":red[**變為 {mult:.1f} 倍**]"


def mult_tag(mult, is_quiz):
    if is_quiz:
        return "?"
    if abs(mult - 1.0) < 1e-4:
        return "1"
    return f"{mult:g}"


col_base_math, col_exp_math = st.columns(2)

# 左欄：基準組
with col_base_math:
    st.markdown(r"#### 📘 【基準對照組】定量關係 ($1.0P\text{ atm}$, $1.0V_{\text{劑}}$)")

    with st.container(border=True):
        st.markdown(r"**1. $V_1 - V_2 = \text{溶解氣體體積 }(\Delta V)$**")
        st.latex(r"P_{\text{O}_2} \Delta V = n_{\text{O}_2} R T")
        st.markdown(r"基準狀態： $\Delta V = 1.0\text{ 倍}$")

    with st.container(border=True):
        st.markdown(r"**2. 此時水中 $C_{M(\text{O}_2)}$ 即為 $\text{O}_2$ 之溶解度 $s$**")
        st.latex(r"s = K_{\text{H}} \times P_{\text{O}_2}")
        st.markdown(r"基準狀態： $s = 1.0\text{ 倍}$")

    with st.container(border=True):
        st.markdown(r"**3. 溶解氣體莫耳數 ($n_{\text{O}_2}$)**")
        st.latex(r"n_{\text{O}_2} = s \times V_{\text{劑}} = K_{\text{H}} \times P_{\text{O}_2} \times V_{\text{劑}}")
        st.markdown(r"基準狀態： $n_{\text{O}_2} = 1.0\text{ 倍}$")

    with st.container(border=True):
        st.markdown(r"**4. 溶解氣體質量 ($W_{\text{O}_2}$)**")
        st.latex(r"W_{\text{O}_2} = n_{\text{O}_2} \times M_{\text{O}_2} = K_{\text{H}} \times P_{\text{O}_2} \times V_{\text{劑}} \times M_{\text{O}_2}")
        st.markdown(r"基準狀態： $W_{\text{O}_2} = 1.0\text{ 倍}$")

# 右欄：實驗組
with col_exp_math:
    st.markdown(
        rf"#### 📕 【實驗調整組】定量關係 (${P_ratio:.1f}P\text{{ atm}}$, ${V_solv_ratio:.1f}V_{{\text{{劑}}}}$)"
    )

    p_str = mult_tag(P_ratio, quiz_mode)
    v_str = mult_tag(V_solv_ratio, quiz_mode)
    n_str = mult_tag(n_ratio, quiz_mode)
    dv_str = mult_tag(dv_ratio, quiz_mode)
    s_str = mult_tag(s_ratio, quiz_mode)
    w_str = mult_tag(w_ratio, quiz_mode)

    with st.container(border=True):
        st.markdown(r"**1. $V_1 - V_2 = \text{溶解氣體體積 }(\Delta V)$**")
        st.latex(
            rf"\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}} \cdot "
            rf"\underbrace{{\Delta V}}_{{\times {dv_str}}} = "
            rf"\underbrace{{n_{{\text{{O}}_2}}}}_{{\times {n_str}}} R T"
        )
        st.markdown(
            rf"👉 溶解氣體體積 ($\Delta V$)：{badge_text(dv_ratio, quiz_mode)}"
        )

    with st.container(border=True):
        st.markdown(r"**2. 此時水中 $C_{M(\text{O}_2)}$ 即為 $\text{O}_2$ 之溶解度 $s$**")
        st.latex(
            rf"\underbrace{{s}}_{{\times {s_str}}} = "
            rf"\underbrace{{K_{{\text{{H}}}}}}_{{\text{{定溫不變}}}} \times "
            rf"\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}}"
        )
        st.markdown(
            rf"👉 氣體溶解度 ($s$)：{badge_text(s_ratio, quiz_mode)}"
        )

    with st.container(border=True):
        st.markdown(r"**3. 溶解氣體莫耳數 ($n_{\text{O}_2}$)**")
        st.latex(
            rf"\underbrace{{n_{{\text{{O}}_2}}}}_{{\times {n_str}}} = "
            rf"K_{{\text{{H}}}} \times "
            rf"\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}} \times "
            rf"\underbrace{{V_{{\text{{劑}}}}}}_{{\times {v_str}}}"
        )
        st.markdown(
            rf"👉 溶解莫耳數 ($n_{{\text{{O}}_2}}$)：{badge_text(n_ratio, quiz_mode)}"
        )

    with st.container(border=True):
        st.markdown(r"**4. 溶解氣體質量 ($W_{\text{O}_2}$)**")
        st.latex(
            rf"\underbrace{{W_{{\text{{O}}_2}}}}_{{\times {w_str}}} = "
            rf"K_{{\text{{H}}}} \times "
            rf"\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}} \times "
            rf"\underbrace{{V_{{\text{{劑}}}}}}_{{\times {v_str}}} \times "
            rf"\underbrace{{M_{{\text{{O}}_2}}}}_{{\text{{分子量不變}}}}"
        )
        st.markdown(
            rf"👉 溶解氣體質量 ($W_{{\text{{O}}_2}}$)：{badge_text(w_ratio, quiz_mode)}"
        )
