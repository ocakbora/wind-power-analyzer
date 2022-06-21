import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np
from datetime import datetime, timezone, date
from scipy import stats
from PIL import Image


#st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

st.title('Windscore')
st.subheader("**A tool for analyzing wind energy**")
st.write("This is an app designed to analyze energy output from a Windprofil.")
st.write("The core functions of this app should be : 1. Upload raw windspeed data, 2. Calculate the power output from this wind speed profil. 3. Calculate the power of a wind farm based on location information. 4. Calculation LCOE")

#@st.cache
def load_data(file):
    df = pd.read_csv(file,sep=",")
    df["Datetime"] = pd.to_datetime(dict(year = df.YEAR,
                                         month = df.MO,
                                         day = df.DY,
                                         hour = df.HR))
    df.set_index("Datetime", inplace = True)
    df = df[["MO","WD50M","WS50M"]]
    df.columns = ["Month","Direction","Speed"]
    return df

#@st.cache
def plot_FFT(df):
    fft = abs(pd.Series(np.fft.rfft(df - df.mean()),
    index = np.fft.rfftfreq(len(df), d = 1./8760))**2)
    fft.plot()
    plt.xlim(0, 768)
    plt.xlabel("1/a")
    plt.grid(True)

with st.sidebar:
    st.subheader("Upload raw data")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = load_data(uploaded_file)
        st.write(dataframe)
    
    st.subheader('Raw data')
    show_raw_data = st.checkbox('Show Raw Data')
    
    st.subheader("Statistic")
    show_statistic = st.checkbox("Show Statistic")    
    
    st.subheader("Plotts")
    show_plot = st.checkbox("Show Plotts")  
    
    st.subheader("Anlagenparameter")
    option = st.selectbox('Windkraftanlagen', ('Enercon E30', 'Siemens', 'Nordex'))

    st.write('You selected:', option)
    st.subheader("Wirtschaftlichkeit")
    
if show_raw_data:
    st.subheader("Raw Data")
    st.dataframe(data = dataframe)

if show_statistic:
    st.subheader("Statistic")
    st.write(dataframe.describe())
    
if show_plot:
    st.header("Plotts")

    #Plott1
    st.subheader("Time-Series")
    fig, ax = plt.subplots()
    dataframe["Speed"].plot(label="Speed [m/s]")
    daily = dataframe["Speed"].resample('D').mean()
    daily.plot(color="#BB0000", label="Daily Mean")
    ax.legend()
    ax.grid(color="black")
    st.pyplot(fig)
  

    #Plott2
    st.subheader("Fast-Fourier Transformation")
    fig, ax = plt.subplots()
    ax = abs(pd.Series(np.fft.rfft(daily - daily.mean())))
    index = np.fft.rfftfreq(len(daily), d = 1./8760)**2
    ax.plot(grid=True)
    st.pyplot(fig)
    
    #Plott3
    st.subheader("Wind speed distribution")
    image = Image.open('/Users/javkhlanenkhbold/Documents/wind-power-analyzer/rawdata/Weibull-Distribution.png')
    st.image(image, caption='Weibull-Distribution')
    fig, ax = plt.subplots()
    dist = stats.weibull_min.fit(daily, floc=0, scale=2)
    speed_range = np.arange(0, daily.max())
    ax.plot(stats.weibull_min.pdf(speed_range, *(dist)),
         color = "blue",
        label = "Weibull Distribution k = {}".format(round(dist[0], 2)))
    ax.set_xlabel("Wind speed [m/s]")
    ax.set_ylabel("Probability")
    ax.hist(daily, bins=np.linspace(0, daily.max()), edgecolor='black', density=True, stacked=True, alpha=0.5, label="Daily Wind data")
    ax.grid(color="black", alpha=0.5) 
    ax.legend()
    st.pyplot(fig)





