import json
import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# 저장할 파일 경로 (작업공간 내)
HIGHSCORE_FILE = "/workspaces/240914seojimin/highscore.json"

# 쿼리 파라미터로 제출된 점수 처리
params = st.experimental_get_query_params()
if "submit_score" in params:
    try:
        submitted = int(params["submit_score"][0])
    except Exception:
        submitted = 0
    # 기존 최고점 불러오기
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                best = int(data.get("score", 0))
        except Exception:
            best = 0
    else:
        best = 0

    if submitted > best:
        best = submitted
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"score": best}, f)
        st.success(f"새 최고점수로 갱신되었습니다: {best}")
    else:
        st.info(f"제출된 점수: {submitted} — 현재 최고점수는 {best} 입니다.")
    # 쿼리 제거 (재처리 방지)
    st.experimental_set_query_params()

# 현재 저장된 최고점 불러와서 표시
if os.path.exists(HIGHSCORE_FILE):
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            global_best = int(data.get("score", 0))
    except Exception:
        global_best = 0
else:
    global_best = 0

st.markdown(f"**전체 플레이어 최고점수:** {global_best}")

GAME_HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  body { margin:0; background:#f0f3f7; font-family: sans-serif; }
  #game { display:block; margin:12px auto; background:#87ceeb; border:4px solid #222; border-radius:8px; }
  .overlay { position: absolute; left:12px; top:12px; color:#111; font-weight:600; }
  .hint { position: absolute; right:12px; top:12px; color:#111; opacity:0.9; }
  #submitArea {
    position: absolute; left:50%; transform:translateX(-50%); top:60%;
    display:none; background: rgba(255,255,255,0.95); padding:10px 14px;
    border-radius:8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    text-align:center;
  }
  #submitBtn {
    background:#2b8aef; color:#fff; border:none; padding:8px 12px; border-radius:6px;
    cursor:pointer; font-weight:600; margin-top:8px;
  }
  #submitBtn:hover { filter:brightness(0.95); }
</style>
</head>
<body>
<div style="position:relative; width:800px; margin:0 auto;">
  <canvas id="game" width="800" height="260"></canvas>
  <div class="overlay" id="score">점수: 0</div>
  <div class="hint">스페이스바 또는 클릭으로 점프 — 충돌 시 R로 재시작 (더블 점프 가능)</div>

  <div id="submitArea">
    <div>최종 점수: <strong id="finalScore">0</strong></div>
    <button id="submitBtn">서버에 점수 제출</button>
    <div style="font-size:12px; color:#444; margin-top:6px;">제출하면 전체 플레이어 최고점으로 비교됩니다.</div>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width, H = canvas.height;
let running = true;
let score = 0;
let speed = 3;
let gravity = 0.8;

// player에 jumps 추가 (더블 점프 상태 추적)
const player = { x: 80, y: H - 40, w: 28, h: 36, vy:0, onGround:true, jumps:0 };
let obstacles = [];
let spawnTimer = 0;
let spawnInterval = 90; // frames

// 배경용 구름/새 객체
const clouds = [];
const birds = [];
for(let i=0;i<6;i++){
  clouds.push({
    x: Math.random()*W,
    y: 20 + Math.random()*60,
    scale: 0.8 + Math.random()*1.2,
    speed: 0.3 + Math.random()*0.6
  });
}
for(let i=0;i<4;i++){
  birds.push({
    x: Math.random()*W,
    y: 40 + Math.random()*80,
    dir: Math.random() < 0.5 ? -1 : 1,
    speed: 1 + Math.random()*1.5,
    flap: Math.random()*Math.PI*2
  });
}

function resetGame(){
  running = true;
  score = 0;
  speed = 3;
  player.y = H - 40;
  player.vy = 0;
  player.onGround = true;
  player.jumps = 0;
  obstacles = [];
  spawnTimer = 0;
  spawnInterval = 90;
  document.getElementById('score').innerText = '점수: 0';
  document.getElementById('submitArea').style.display = 'none';
  for(const c of clouds){ c.x = Math.random()*W; c.y = 20 + Math.random()*60; }
  for(const b of birds){ b.x = Math.random()*W; b.y = 40 + Math.random()*80; b.flap = Math.random()*Math.PI*2; }
  loop();
}

function spawnObstacle(){
  const h = 24 + Math.random()*24;
  obstacles.push({ x: W + 20, y: H - h - 8, w: 18 + Math.random()*18, h: h });
}

function update(){
  if(!running) return;

  // 배경 업데이트 (구름/새)
  for(const c of clouds){
    c.x -= c.speed * (speed/3);
    if(c.x + 120*c.scale < 0) c.x = W + 20 + Math.random()*80;
  }
  for(const b of birds){
    b.x -= b.speed * (speed/3) * b.dir;
    b.flap += 0.25 + Math.random()*0.15;
    if(b.dir < 0 && b.x < -30) { b.x = W + 30; b.y = 30 + Math.random()*100; }
    if(b.dir > 0 && b.x > W + 30) { b.x = -30; b.y = 30 + Math.random()*100; }
  }

  // player physics
  player.vy += gravity;
  player.y += player.vy;
  if(player.y + player.h >= H - 8){
    player.y = H - 8 - player.h;
    player.vy = 0;
    player.onGround = true;
    player.jumps = 0; // 착지하면 점프 카운트 리셋
  } else {
    player.onGround = false;
  }

  // obstacles
  spawnTimer++;
  if(spawnTimer > spawnInterval){
    spawnTimer = 0;
    spawnInterval = 60 + Math.floor(Math.random()*70);
    spawnObstacle();
  }
  for(let i=obstacles.length-1;i>=0;i--){
    obstacles[i].x -= speed;
    if(obstacles[i].x + obstacles[i].w < 0) obstacles.splice(i,1);
  }

  // collision
  for(const ob of obstacles){
    if(player.x < ob.x + ob.w &&
       player.x + player.w > ob.x &&
       player.y < ob.y + ob.h &&
       player.y + player.h > ob.y){
         running = false;
         // 게임 오버 시 제출 영역 노출
         const final = Math.floor(score/10);
         document.getElementById('finalScore').innerText = final;
         document.getElementById('submitArea').style.display = 'block';
    }
  }

  // score & difficulty
  score += 1;
  if(score % 500 === 0) speed += 0.5;
  document.getElementById('score').innerText = '점수: ' + Math.floor(score/10);
}

function draw(){
  // sky gradient
  const g = ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0, '#87cefa');
  g.addColorStop(0.6, '#aee0ff');
  g.addColorStop(1, '#87ceeb');
  ctx.fillStyle = g;
  ctx.fillRect(0,0,W,H);

  // 먼 배경 구름
  for(const c of clouds){
    ctx.save();
    ctx.translate(c.x, c.y);
    ctx.scale(c.scale, c.scale);
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.beginPath();
    ctx.arc(0, 0, 18, Math.PI*0.5, Math.PI*1.5);
    ctx.arc(22, -8, 22, Math.PI*1.0, Math.PI*1.85);
    ctx.arc(44, 0, 18, Math.PI*1.5, Math.PI*0.5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // 새 그리기
  for(const b of birds){
    const wing = Math.sin(b.flap) * 6;
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(b.x, b.y);
    ctx.lineTo(b.x + 8 * b.dir, b.y + wing);
    ctx.lineTo(b.x + 16 * b.dir, b.y);
    ctx.stroke();
  }

  // ground
  ctx.fillStyle = '#5c3a21';
  ctx.fillRect(0,H-8,W,8);
  ctx.fillStyle = '#8b5a2b';
  ctx.fillRect(0,H-40,W,32);

  // player
  ctx.fillStyle = '#ff4757';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  // simple eye
  ctx.fillStyle = '#111';
  ctx.fillRect(player.x + player.w - 10, player.y + 8, 4, 4);

  // obstacles
  ctx.fillStyle = '#2f3542';
  for(const ob of obstacles){
    ctx.fillRect(ob.x, ob.y, ob.w, ob.h);
  }

  if(!running){
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(0,0,W,H);
    ctx.fillStyle = '#fff';
    ctx.font = '24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('게임 오버', W/2, H/2 - 10);
    ctx.font = '16px sans-serif';
    ctx.fillText("R 키를 눌러 재시작", W/2, H/2 + 20);
    ctx.textAlign = 'left';
  }
}

function loop(){
  update();
  draw();
  if(running) requestAnimationFrame(loop);
}

// 더블 점프 지원
function jump(){
  if(player.onGround){
    player.vy = -12;
    player.onGround = false;
    player.jumps = 1;
  } else if(player.jumps < 2){
    player.vy = -10;
    player.jumps++;
  }
}

document.addEventListener('keydown', (e)=>{
  if(e.code === 'Space'){ e.preventDefault(); jump(); }
  if(!running && (e.key === 'r' || e.key === 'R')) resetGame();
});
canvas.addEventListener('mousedown', ()=> jump());
canvas.addEventListener('touchstart', ()=> { jump(); });

// 제출 버튼 동작: top 으로 쿼리 파라미터를 붙여 제출
document.getElementById('submitBtn').addEventListener('click', function(){
  const final = document.getElementById('finalScore').innerText || '0';
  const qs = '?submit_score=' + encodeURIComponent(final);
  try {
    // 부모 창의 origin+pathname으로 안전하게 URL 구성 (cross-origin 접근 시 예외 발생할 수 있음)
    const topLoc = window.top.location;
    const baseOrigin = topLoc.origin ? topLoc.origin : window.location.origin;
    const basePath = topLoc.pathname ? topLoc.pathname : window.location.pathname;
    window.top.location.href = baseOrigin + basePath + qs;
  } catch (e) {
    // 부모 창에 접근 불가하면 현재 창의 origin+pathname으로 대체
    const base = window.location.origin + window.location.pathname;
    window.location.href = base + qs;
  }
});

loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=360, scrolling=False)

# 게임 설명 추가
st.header("🎮 게임 설명")
st.markdown("""
- **목표:** 허들을 점프해서 피하며 최대한 오래 달리기.
- **조작:** 스페이스바 또는 캔버스 클릭/터치로 점프. 충돌 시 `R` 키로 재시작.
- **점수:** 시간이 지날수록 증가하며 화면 왼쪽 상단에 표시됩니다(초 단위 환산).
- **난이도:** 시간이 지남에 따라 장애물 속도가 빨라집니다.
- **팁:** 착지한 후에만 다시 점프할 수 있으므로 타이밍을 잘 맞추세요. (더블 점프: 공중에서 한 번 더 점프 가능)
- **모바일:** 터치로도 점프 가능합니다.
""")
