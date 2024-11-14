import streamlit as st
import FallModel

st.write("Fall Detection")

st.button("Start Camera", on_click=FallModel.getVideoFeed())

