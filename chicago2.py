import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


st.title("NYC/Chicago Crime Visualization")
st.header('By Faraz Younus | M.S. Stats & Data Science', divider='gray')

def load_dataframe(file_path, city):
    df = pd.read_csv(file_path)
    if city == "Chicago Crime":
        # Assign latitude and longitude values for Chicago
        latvalue = 41.81184357
        lonvalue = -87.60681861
    else:  # Assuming the other city is NYC Crime
        # Assign latitude and longitude values for NYC
        latvalue = 40.7569
        lonvalue = -73.8757
    return df, latvalue, lonvalue

dataframe_paths = {
    "Chicago Crime": "chicago.csv",
    "NYC Crime": "nyccrime.csv"
}

selected_dataframes = st.sidebar.multiselect("Select one City for Map", list(dataframe_paths.keys()))
for city in selected_dataframes:
    st.write(f"Showing: {city}")
    df, latvalue, lonvalue = load_dataframe(dataframe_paths[city], city)
    

    df['Date'] = pd.to_datetime(df['Date'])
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()


    default_start_date = min_date
    default_end_date = max_date

    selected_start_date, selected_end_date = st.sidebar.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(default_start_date, default_end_date)
    )

    crime_types = df['Primary Type'].unique()
    selected_crime_types = st.sidebar.multiselect(
        "Select crime types",
        crime_types,
        default=None
    )

    descriptions = df[df['Primary Type'].isin(selected_crime_types)]['Description'].unique()
    selected_descriptions = st.sidebar.multiselect(
        "Select descriptions",
        descriptions,
        default=descriptions
    )

    st.sidebar.write("Selected start date:", selected_start_date)
    st.sidebar.write("Selected end date:", selected_end_date)

    filtered_df = df[
        (df['Date'] >= pd.to_datetime(selected_start_date)) & 
        (df['Date'] <= pd.to_datetime(selected_end_date)) &
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


