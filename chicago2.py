import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


st.title("NYC/Chicago Crime Visualization")
st.header('By Faraz Younus | M.S. Stats & Data Science', divider='gray')
st.markdown("### Open the upper left corner sidebar to select city!")


@st.cache
def load_dataframe(file_path):
    # Load the data and preprocess it once
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])  # Convert the date once
    return df

dataframe_paths = {
    "Chicago Crime": "chicago.csv",
    "NYC Crime": "nyccrime.csv"
}

# Load data once
dataframes = {city: load_dataframe(path) for city, path in dataframe_paths.items()}

selected_cities = st.sidebar.multiselect("Select one City for Map", list(dataframe_paths.keys()))

for city in selected_cities:
    df = dataframes[city]
    latvalue, lonvalue = (41.81184357, -87.60681861) if city == "Chicago Crime" else (40.7569, -73.8757)
    
    min_date, max_date = df['Date'].min(), df['Date'].max()

    # Use date range directly
    selected_start_date, selected_end_date = st.sidebar.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    # Handling the crime types and descriptions more efficiently
    if 'selected_crime_types' not in st.session_state:
        st.session_state.selected_crime_types = df['Primary Type'].unique()

    selected_crime_types = st.sidebar.multiselect(
        "Select crime types",
        df['Primary Type'].unique(),
        default=st.session_state.selected_crime_types
    )

    descriptions = df[df['Primary Type'].isin(selected_crime_types)]['Description'].unique()
    selected_descriptions = st.sidebar.multiselect(
        "Select descriptions",
        descriptions,
        default=descriptions
    )

    # Filtering data efficiently
    filtered_df = df[
        (df['Date'] >= selected_start_date) & 
        (df['Date'] <= selected_end_date) &
        (df['Primary Type'].isin(selected_crime_types)) &
        (df['Description'].isin(selected_descriptions))
    ]

    
    st.write(filtered_df)



    st.header('Stats')
    number_of_crimes = len(filtered_df)
    st.metric(label="Number of Arrests", value=number_of_crimes)



    st.header('Line Chart', divider='gray')
    crime_counts_by_date = filtered_df.groupby(['Date', 'Primary Type']).size().unstack(fill_value=0)
    st.line_chart(crime_counts_by_date)



    st.header('Map', divider='gray')
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=latvalue,
            longitude=lonvalue,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=filtered_df,
                get_position='[lon, lat]',
                radius=100,
                elevation_scale=3,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
            ),
        ],
    ))


