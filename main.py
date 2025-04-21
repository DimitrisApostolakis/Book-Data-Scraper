import streamlit as st
import pandas as pd

df = pd.read_csv("./csv/updated_bookshelf.csv")

st.title("Loading...")

st.dataframe(df)