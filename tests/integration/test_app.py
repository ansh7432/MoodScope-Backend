import streamlit as st

st.title("🎵 MoodScope Test")
st.write("If you can see this, Streamlit is working!")

st.success("✅ App is loading correctly")

if st.button("Test Button"):
    st.balloons()
    st.write("🎉 Button works!")
