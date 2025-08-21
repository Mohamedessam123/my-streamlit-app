import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    df = pd.read_csv("Payment.csv")
    return df

df = load_data()

st.write(df.head())

with st.sidebar:
    st.header("🔎 Filter Options")
    
    your_choice = st.multiselect("Select Column", df.columns.tolist(), default=None,max_selections=1)
    col1 = df.columns[0]

    if your_choice:
        selected_column = your_choice[0]
        st.write("You selected:", selected_column)
        st.write("first columns has", df[col1].unique())
    