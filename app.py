import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="亨利定律互動模擬", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

/* 只固定下方定量關係區的卡片高度，頂部控制面板不受影響 */
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
    box-sizing: border-box;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] > div {
    box-sizing: border-box;
}

/* 公式區左右欄的每張卡片使用一致高度，讓同列上下邊界對齊 */
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
    min-height: 218px;
}

/* 公式區維持一致的內距與段落間距 */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.55rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stLatex"] {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### 亨利定律整理：於定溫、相同難溶性氣體之情況，該難溶性氣體之分壓與溶解度成正比")

# 頂部控制面板
with st.container(border=True):
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.5, 1.5, 1.2, 1.2])
    if "p_val" not in st.session_state:
        st.session_state.p_val = 2.0
    if "v_val" not in st.session_state:
        st.session_state.v_val = 1.0

    with ctrl_col3:
        st.markdown("**⚡ 快速套用課本情境**")
        b1, b2, b3 = st.columns(3)
        if b1.button("1P, 1V", use_container_width=True):
            st.session_state.p_val, st.session_state.v_val = 1.0, 1.0
        if b2.button("2P, 1V", use_container_width=True):
            st.session_state.p_val, st.session_state.v_val = 2.0, 1.0
        if b3.button("1P, 2V", use_container_width=True):
            st.session_state.p_val, st.session_state.v_val = 1.0, 2.0

    with ctrl_col1:
        P_ratio = st.slider("🔹 【實驗組】氣體分壓 (P 倍數)",
                            min_value=0.5, max_value=3.0, step=0.1, key="p_val")
    with ctrl_col2:
        V_solv_ratio = st.slider("💧 【實驗組】溶劑體積 (V劑 倍數)",
                                 min_value=0.5, max_value=2.5, step=0.1, key="v_val")
    with ctrl_col4:
        st.markdown("**🛠️ 教學輔助設定**")
        quiz_mode = st.checkbox("🔒 遮蔽變化結論 (提問模式)", value=False)
        anim_speed = st.slider("粒子移動速度", 0.0, 3.0, 1.2, 0.2, label_visibility="collapsed")

s_ratio = P_ratio
n_ratio = s_ratio * V_solv_ratio
w_ratio = n_ratio
dv_ratio = n_ratio / P_ratio

def render_dual_canvas(P_exp, V_exp, dV_exp, speed):
    html_code = f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{margin:0;background:transparent;font-family:'Microsoft JhengHei','PingFang TC',sans-serif}}
#canvas-wrap{{width:100%;background:#fff;border:2px solid #dcdcdc;border-radius:12px;box-sizing:border-box;overflow:hidden}}
canvas{{width:100%;height:auto;display:block}}
</style></head><body><div id="canvas-wrap"><canvas id="simCanvas"></canvas></div>
<script>
const canvas=document.getElementById('simCanvas'),ctx=canvas.getContext('2d');
const W=1400,H=540,dpr=window.devicePixelRatio||1;
canvas.width=W*dpr;canvas.height=H*dpr;ctx.scale(dpr,dpr);
const P_EXP={P_exp},V_EXP={V_exp},DV_EXP={dV_exp},SPEED={speed};
const BOTTOM=495,TOP=75,CW=200,PH=18,LIQH=65,GASH=115,DVH=48;
function createParticles(n,x1,x2,y1,y2,phase){{
 const a=[],r=5;
 for(let i=0;i<n;i++){{
  const ang=Math.random()*Math.PI*2,v=(1.1+Math.random()*1.1)*(phase==='liq'?0.7:1);
  a.push({{x:x1+r+Math.random()*(x2-x1-2*r),y:y1+r+Math.random()*(y2-y1-2*r),
   vx:Math.cos(ang)*v,vy:Math.sin(ang)*v,r,xMin:x1,xMax:x2,yMin:y1,yMax:y2}});
 }}return a;
}}
function buildGroup(off,p,v,dv,title,color){{
 const hL=LIQH*v,yL=BOTTOM-hL,yEq=yL-GASH,hD=DVH*dv,yInit=yEq-hD,x1=off+55,x2=off+385;
 const nl=Math.max(2,Math.round(5*p*v)),ng=Math.max(3,Math.round(10*p));
 return {{off,p,v,dv,title,color,x1,x2,hL,yL,yEq,hD,yInit,
 init:createParticles(ng+nl,x1,x1+CW,yInit+PH,yL,'gas'),
 gas:createParticles(ng,x2,x2+CW,yEq+PH,yL,'gas'),
 liq:createParticles(nl,x2,x2+CW,yL,BOTTOM,'liq')}};
}}
const base=buildGroup(15,1,1,1,"【基準對照組】 1.0 P atm、1.0 V劑","#2b579a");
const exp=buildGroup(715,P_EXP,V_EXP,DV_EXP,`【實驗調整組】 ${{P_EXP.toFixed(1)}} P atm、${{V_EXP.toFixed(1)}} V劑`,"#b02a37");
function arrow(x1,y1,x2,y2,c="#000",lw=2){{
 const h=9,a=Math.atan2(y2-y1,x2-x1);ctx.strokeStyle=c;ctx.fillStyle=c;ctx.lineWidth=lw;
 ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x2,y2);ctx.lineTo(x2-h*Math.cos(a-Math.PI/6),y2-h*Math.sin(a-Math.PI/6));
 ctx.lineTo(x2-h*Math.cos(a+Math.PI/6),y2-h*Math.sin(a+Math.PI/6));ctx.closePath();ctx.fill();
}}
function doubleArrow(x,y1,y2,c){{arrow(x,(y1+y2)/2,x,y1,c,2);arrow(x,(y1+y2)/2,x,y2,c,2)}}

// 平衡容器中：氣相與液相粒子可以跨越界面，雙向交換
function updatePhase(g,phase){{
 const arr=phase==='gas'?g.gas:g.liq,other=phase==='gas'?g.liq:g.gas;
 const interfaceY=g.yL,gasBottom=g.yEq+PH,prob=Math.min(0.22,0.035*SPEED);
 for(let i=arr.length-1;i>=0;i--){{
  const p=arr[i];p.x+=p.vx*SPEED;p.y+=p.vy*SPEED;
  if(p.x-p.r<p.xMin+2){{p.x=p.xMin+p.r+2;p.vx=Math.abs(p.vx)}}
  if(p.x+p.r>p.xMax-2){{p.x=p.xMax-p.r-2;p.vx=-Math.abs(p.vx)}}
  if(phase==='gas'){{
   if(p.y+p.r>=interfaceY && p.vy>0){{
    if(Math.random()<prob){{
     arr.splice(i,1);p.y=interfaceY+p.r+1;p.yMin=interfaceY;p.yMax=BOTTOM;
     p.vx*=0.7;p.vy=Math.max(0.45,Math.abs(p.vy)*0.7);other.push(p);continue;
    }}else{{p.y=interfaceY-p.r-1;p.vy=-Math.abs(p.vy)}}
   }}
   if(p.y-p.r<gasBottom){{p.y=gasBottom+p.r;p.vy=Math.abs(p.vy)}}
  }}else{{
   if(p.y-p.r<=interfaceY && p.vy<0){{
    if(Math.random()<prob){{
     arr.splice(i,1);p.y=interfaceY-p.r-1;p.yMin=gasBottom;p.yMax=interfaceY;
     p.vx/=0.7;p.vy=-Math.max(0.45,Math.abs(p.vy)/0.7);other.push(p);continue;
    }}else{{p.y=interfaceY+p.r+1;p.vy=Math.abs(p.vy)}}
   }}
   if(p.y+p.r>BOTTOM){{p.y=BOTTOM-p.r;p.vy=-Math.abs(p.vy)}}
  }}
  ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle="#111";ctx.fill();
 }}
}}
function drawStaticParticles(a){{
 for(const p of a){{
  p.x+=p.vx*SPEED;p.y+=p.vy*SPEED;
  if(p.x-p.r<p.xMin+2||p.x+p.r>p.xMax-2)p.vx*=-1;
  if(p.y-p.r<p.yMin+2||p.y+p.r>p.yMax-2)p.vy*=-1;
  p.x=Math.max(p.xMin+p.r+2,Math.min(p.xMax-p.r-2,p.x));
  p.y=Math.max(p.yMin+p.r+2,Math.min(p.yMax-p.r-2,p.y));
  ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle="#111";ctx.fill();
 }}
}}
function drawGroup(g){{
 const pt=g.p===1?"P atm":`${{g.p.toFixed(1)}}P atm`,vt=g.v===1?"V劑":`${{g.v.toFixed(1)}}V劑`;
 ctx.fillStyle=g.color;ctx.font="bold 20px Microsoft JhengHei";ctx.textAlign="center";ctx.fillText(g.title,g.off+335,32);
 ctx.fillStyle="#555";ctx.font="bold 15px Microsoft JhengHei";
 ctx.fillText("剛接觸瞬間（未溶解）",g.x1+CW/2,60);ctx.fillText("溶解達平衡狀態",g.x2+CW/2,60);
 // 初始容器液體與活塞
 ctx.fillStyle="#b8daff";ctx.fillRect(g.x1,g.yL,CW,g.hL);ctx.strokeStyle="#333";ctx.lineWidth=1.5;ctx.strokeRect(g.x1,g.yL,CW,g.hL);
 ctx.fillStyle="#003366";ctx.font="bold 18px Microsoft JhengHei";ctx.fillText(vt,g.x1+CW/2,g.yL+g.hL/2+7);
 ctx.fillStyle="#a6a6a6";ctx.fillRect(g.x1,g.yInit,CW,PH);ctx.strokeStyle="#222";ctx.lineWidth=2;ctx.strokeRect(g.x1,g.yInit,CW,PH);
 arrow(g.x1+CW/2,g.yInit-45,g.x1+CW/2,g.yInit-2);
 ctx.fillStyle="#000";ctx.textAlign="left";ctx.font="bold 16px Microsoft JhengHei";ctx.fillText(pt,g.x1+CW/2+8,g.yInit-18);
 drawStaticParticles(g.init);
 ctx.fillText(`P O₂ = ${{pt}}`,g.x1+10,g.yInit+42);ctx.textAlign="right";ctx.fillText("V₁",g.x1+CW-10,g.yL-12);
 ctx.strokeStyle="#000";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(g.x1,TOP);ctx.lineTo(g.x1,BOTTOM);ctx.lineTo(g.x1+CW,BOTTOM);ctx.lineTo(g.x1+CW,TOP);ctx.stroke();
 ctx.fillStyle="#000";ctx.textAlign="center";ctx.font="bold 16px Microsoft JhengHei";ctx.fillText("溶解達平衡",g.x1+CW+65,290);arrow(g.x1+CW+15,305,g.x2-15,305);
 // 平衡容器
 ctx.fillStyle="#b8daff";ctx.fillRect(g.x2,g.yL,CW,g.hL);ctx.strokeStyle="#333";ctx.lineWidth=1.5;ctx.strokeRect(g.x2,g.yL,CW,g.hL);
 ctx.save();ctx.setLineDash([5,5]);ctx.strokeStyle="#666";ctx.lineWidth=1.8;ctx.strokeRect(g.x2,g.yInit,CW,PH);ctx.restore();
 ctx.fillStyle="#a6a6a6";ctx.fillRect(g.x2,g.yEq,CW,PH);ctx.strokeStyle="#222";ctx.lineWidth=2;ctx.strokeRect(g.x2,g.yEq,CW,PH);
 arrow(g.x2+CW/2,g.yEq-45,g.x2+CW/2,g.yEq-2);
 ctx.fillStyle="#000";ctx.textAlign="left";ctx.font="bold 16px Microsoft JhengHei";ctx.fillText(pt,g.x2+CW/2+8,g.yEq-18);
 ctx.fillStyle="#111";updatePhase(g,"gas");updatePhase(g,"liq");
 ctx.fillStyle="#003366";ctx.textAlign="center";ctx.font="bold 18px Microsoft JhengHei";ctx.fillText(vt,g.x2+CW/2,g.yL+g.hL/2+7);
 ctx.fillStyle="#111";ctx.textAlign="left";ctx.font="bold 16px Microsoft JhengHei";ctx.fillText(`P O₂ = ${{pt}}`,g.x2+10,g.yEq+42);
 ctx.textAlign="right";ctx.fillText("V₂",g.x2+CW-10,g.yL-12);
 ctx.strokeStyle="#000";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(g.x2,TOP);ctx.lineTo(g.x2,BOTTOM);ctx.lineTo(g.x2+CW,BOTTOM);ctx.lineTo(g.x2+CW,TOP);ctx.stroke();
 const dx=g.x2+CW+22;doubleArrow(dx,g.yInit+PH/2,g.yEq+PH/2,"#d9534f");
 ctx.fillStyle="#d9534f";ctx.textAlign="left";ctx.font="bold 17px Microsoft JhengHei";ctx.fillText("ΔV",dx+8,(g.yInit+g.yEq+PH)/2+6);
}}
function animate(){{
 ctx.clearRect(0,0,W,H);ctx.save();ctx.strokeStyle="#ccc";ctx.lineWidth=2;ctx.setLineDash([8,6]);ctx.beginPath();ctx.moveTo(700,15);ctx.lineTo(700,H-15);ctx.stroke();ctx.restore();
 drawGroup(base);drawGroup(exp);requestAnimationFrame(animate);
}}
animate();
</script></body></html>
"""
    return html_code

components.html(render_dual_canvas(P_ratio, V_solv_ratio, dv_ratio, anim_speed), height=555, scrolling=False)

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

# 定量關係：左右兩欄使用相同卡片結構與順序
col_base, col_exp = st.columns(2, gap="medium")

with col_base:
    st.markdown(r"#### 📘【基準對照組】定量關係（1.0 P atm、1.0 V劑）")
    with st.container(border=True):
        st.markdown(r"**1. $V_1-V_2=\text{溶解氣體體積 }(\Delta V)$**")
        st.latex(r"P_{\text{O}_2}\Delta V=n_{\text{O}_2}RT")
        st.markdown(r"基準狀態： $\Delta V=1.0\text{ 倍}$")
    with st.container(border=True):
        st.markdown(r"**2. 此時水中 $C_{M(\text{O}_2)}$ 即為 $\text{O}_2$ 之溶解度 $s$**")
        st.latex(r"s=K_{\text{H}}\times P_{\text{O}_2}")
        st.markdown(r"基準狀態： $s=1.0\text{ 倍}$")
    with st.container(border=True):
        st.markdown(r"**3. 溶解氣體莫耳數 ($n_{\text{O}_2}$)**")
        st.latex(r"n_{\text{O}_2}=s\times V_{\text{劑}}=K_{\text{H}}\times P_{\text{O}_2}\times V_{\text{劑}}")
        st.markdown(r"基準狀態： $n_{\text{O}_2}=1.0\text{ 倍}$")
    with st.container(border=True):
        st.markdown(r"**4. 溶解氣體質量 ($W_{\text{O}_2}$)**")
        st.latex(r"W_{\text{O}_2}=n_{\text{O}_2}\times M_{\text{O}_2}=K_{\text{H}}\times P_{\text{O}_2}\times V_{\text{劑}}\times M_{\text{O}_2}")
        st.markdown(r"基準狀態： $W_{\text{O}_2}=1.0\text{ 倍}$")

with col_exp:
    st.markdown(rf"#### 📕【實驗調整組】定量關係（{P_ratio:.1f} P atm、{V_solv_ratio:.1f} V劑）")
    p_str, v_str = mult_tag(P_ratio, quiz_mode), mult_tag(V_solv_ratio, quiz_mode)
    n_str, dv_str = mult_tag(n_ratio, quiz_mode), mult_tag(dv_ratio, quiz_mode)
    s_str, w_str = mult_tag(s_ratio, quiz_mode), mult_tag(w_ratio, quiz_mode)
    with st.container(border=True):
        st.markdown(r"**1. $V_1-V_2=\text{溶解氣體體積 }(\Delta V)$**")
        st.latex(rf"\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}}\cdot\underbrace{{\Delta V}}_{{\times {dv_str}}}=\underbrace{{n_{{\text{{O}}_2}}}}_{{\times {n_str}}}RT")
        st.markdown(rf"👉 溶解氣體體積 ($\Delta V$)：{badge_text(dv_ratio, quiz_mode)}")
    with st.container(border=True):
        st.markdown(r"**2. 此時水中 $C_{M(\text{O}_2)}$ 即為 $\text{O}_2$ 之溶解度 $s$**")
        st.latex(rf"\underbrace{{s}}_{{\times {s_str}}}= \underbrace{{K_{{\text{{H}}}}}}_{{\text{{定溫不變}}}}\times\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}}")
        st.markdown(rf"👉 氣體溶解度 ($s$)：{badge_text(s_ratio, quiz_mode)}")
    with st.container(border=True):
        st.markdown(r"**3. 溶解氣體莫耳數 ($n_{\text{O}_2}$)**")
        st.latex(rf"\underbrace{{n_{{\text{{O}}_2}}}}_{{\times {n_str}}}=K_{{\text{{H}}}}\times\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}}\times\underbrace{{V_{{\text{{劑}}}}}}_{{\times {v_str}}}")
        st.markdown(rf"👉 溶解莫耳數 ($n_{{\text{{O}}_2}}$)：{badge_text(n_ratio, quiz_mode)}")
    with st.container(border=True):
        st.markdown(r"**4. 溶解氣體質量 ($W_{\text{O}_2}$)**")
        st.latex(rf"\underbrace{{W_{{\text{{O}}_2}}}}_{{\times {w_str}}}=K_{{\text{{H}}}}\times\underbrace{{P_{{\text{{O}}_2}}}}_{{\times {p_str}}}\times\underbrace{{V_{{\text{{劑}}}}}}_{{\times {v_str}}}\times\underbrace{{M_{{\text{{O}}_2}}}}_{{\text{{分子量不變}}}}")
        st.markdown(rf"👉 溶解氣體質量 ($W_{{\text{{O}}_2}}$)：{badge_text(w_ratio, quiz_mode)}")
