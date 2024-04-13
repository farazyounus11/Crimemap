import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("NYC/Chicago Crime Visualization")
st.markdown("### Open the upper left corner sidebar to select city!")

@st.cache
def load_dataframe(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

dataframe_paths = {
    "Chicago Crime": "chicago.csv",
    "NYC Crime": "nyccrime.csv"
}

dataframes = {city: load_dataframe(path) for city, path in dataframe_paths.items()}
selected_cities = st.sidebar.multiselect("Select one City for Map", list(dataframe_paths.keys()))

for city in selected_cities:
    df = dataframes[city]
    latvalue, lonvalue = (41.81184357, -87.60681861) if city == "Chicago Crime" else (40.7569, -73.8757)
    
    # Ensure that min_date and max_date are datetime objects and convert to standard Python datetime
    min_date = pd.to_datetime(df['Date'].min()).to_pydatetime()
    max_date = pd.to_datetime(df['Date'].max()).to_pydatetime()
    st.write(f"Min Date Type: {type(min_date)}, Max Date Type: {type(max_date)}")  # Debug statement

    try:
        # Convert the timestamps to Python datetime objects directly for the slider
        selected_start_date, selected_end_date = st.sidebar.slider(
            "Select date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
    except Exception as e:
        st.error(f"Error with slider: {e}")
        continue  # Skip the rest of the loop on error to prevent further issues

    # Handling the crime types and descriptions more efficiently
    crime_types = df['Primary Type'].unique()
    if 'selected_crime_types' not in st.session_state or not st.session_state.selected_crime_types:
        st.session_state.selected_crime_types = crime_types

    selected_crime_types = st.sidebar.multiselect(
        "Select crime types",
        options=crime_types,
        default=st.session_state.none
    )

    # Filter descriptions based on selected crime types
    descriptions = df[df['Primary Type'].isin(selected_crime_types)]['Description']. unique()
    selected_descriptions = st.sidebar.multiselect(
        "Select descriptions",
        options=descriptions,
        default=descriptions
    )

    # Apply filters to dataframe based on user selections
    filtered_df = df[
        (df['Date'] >= selected_start_date) & 
        (df['Date'] <= selected_end_date) &
        (df['Primary Type'].isin(selected_crime_types)) &
        (df['Description'].isin(selected_descriptions))
    ]

    # Display the filtered DataFrame
    st.write(filtered_df)

    # Display stats
    st.header('Stats')
    number_of_crimes = len(filtered_df)
    st.metric(label="Number of Arrests", value=number_of_crimes)

    # Line Chart displaying crimes over time
    st.header('Line Chart', divider='gray')
    crime_counts_by_date = filtered_df.groupby(['Date', 'Primary Type']).size().unstack(fill_value=0)
    st.line_chart(crime_counts_by_date)

    # Map Visualization using PyDeck
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
