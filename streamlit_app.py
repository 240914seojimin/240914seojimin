import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# 아래에 주사위 굴리기 기능 추가
import random
import pandas as pd

st.header("🎲 간단한 주사위 굴리기")

col1, col2 = st.columns(2)
num_dice = col1.slider("주사위 개수", min_value=1, max_value=10, value=2, step=1)
sides = col2.selectbox("면 수 선택", options=[4, 6, 8, 10, 12, 20], index=1)

seed_fix = st.checkbox("시드 고정 (재현 가능)")
seed_value = None
if seed_fix:
    seed_value = st.number_input("시드 값", value=42, step=1)

if st.button("굴려보기"):
    if seed_fix:
        random.seed(int(seed_value))
    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls)
    avg = total / num_dice

    st.subheader("결과")
    st.write("개별 굴림:", rolls)
    st.write(f"합계: {total}  •  평균: {avg:.2f}")

    # 도수표 / 막대그래프
    counts = pd.Series(rolls).value_counts().sort_index()
    df = counts.rename_axis("face").reset_index(name="count").set_index("face")
    st.bar_chart(df["count"])

    # 확률적 기대값(이론값) 표시
    expected = num_dice * (1 + sides) / 2
    st.caption(f"이론적 기대 합계: {expected:.2f}")
