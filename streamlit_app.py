import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# 간단한 러너 + 허들 게임 (스페이스바로 점프)
import streamlit.components.v1 as components

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
</style>
</head>
<body>
<div style="position:relative; width:800px; margin:0 auto;">
  <canvas id="game" width="800" height="200"></canvas>
  <div class="overlay" id="score">점수: 0</div>
  <div class="hint">스페이스바 또는 클릭으로 점프 — 충돌 시 R로 재시작</div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width, H = canvas.height;
let running = true;
let score = 0;
let speed = 3;
let gravity = 0.8;

const player = { x: 80, y: H - 40, w: 28, h: 36, vy:0, onGround:true };
let obstacles = [];
let spawnTimer = 0;
let spawnInterval = 90; // frames

function resetGame(){
  running = true;
  score = 0;
  speed = 3;
  player.y = H - 40;
  player.vy = 0;
  player.onGround = true;
  obstacles = [];
  spawnTimer = 0;
  spawnInterval = 90;
  document.getElementById('score').innerText = '점수: 0';
  loop();
}

function spawnObstacle(){
  const h = 24 + Math.random()*24;
  obstacles.push({ x: W + 20, y: H - h - 8, w: 18 + Math.random()*18, h: h });
}

function update(){
  if(!running) return;

  // player physics
  player.vy += gravity;
  player.y += player.vy;
  if(player.y + player.h >= H - 8){
    player.y = H - 8 - player.h;
    player.vy = 0;
    player.onGround = true;
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
         showGameOver();
    }
  }

  // score & difficulty
  score += 1;
  if(score % 500 === 0) speed += 0.5;
  document.getElementById('score').innerText = '점수: ' + Math.floor(score/10);
}

function draw(){
  // sky
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle = '#87ceeb';
  ctx.fillRect(0,0,W,H);

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
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
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

function jump(){
  if(player.onGround){
    player.vy = -12;
    player.onGround = false;
  }
}

document.addEventListener('keydown', (e)=>{
  if(e.code === 'Space'){ e.preventDefault(); jump(); }
  if(!running && (e.key === 'r' || e.key === 'R')) resetGame();
});
canvas.addEventListener('mousedown', ()=> jump());
canvas.addEventListener('touchstart', ()=> { jump(); });

loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=260, scrolling=False)
