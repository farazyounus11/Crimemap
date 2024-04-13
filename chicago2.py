import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Setting the title and sidebar options for city selection
st.title("NYC/Chicago Crime Visualization")
st.markdown("### Open the upper left corner sidebar to select city!")

@st.cache(allow_output_mutation=True)
def load_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

dataframe_paths = {
    "Chicago Crime": "chicago.csv",
    "NYC Crime": "nyccrime.csv"
}

@st.cache(allow_output_mutation=True)
def get_dataframes():
    return {city: load_dataframe(path) for city, path in dataframe_paths.items()}

dataframes = get_dataframes()
selected_cities = st.sidebar.multiselect("Select one City for Map", list(dataframe_paths.keys()))

for city in selected_cities:
    df = dataframes[city]
    if df.empty:
        st.error("Selected city data is not available or the file is empty.")
        continue

    latvalue, lonvalue = (41.81184357, -87.60681861) if city == "Chicago Crime" else (40.7569, -73.8757)

    try:
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        selected_start_date, selected_end_date = st.sidebar.slider(
            "Select date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
    except Exception as e:
        st.error(f"Error with date slider: {str(e)}")
        continue

    crime_types = df['Primary Type'].unique()
    selected_crime_types = st.sidebar.multiselect("Select crime types", options=crime_types, default=[])

    if selected_crime_types:
        descriptions = df[df['Primary Type'].isin(selected_crime_types)]['Description'].unique()
        selected_descriptions = st.sidebar.multiselect("Select descriptions", options=descriptions, default=descriptions)
    else:
        descriptions = []
        selected_descriptions = []
        st.sidebar.multiselect("Select descriptions", options=descriptions, disabled=True)

    filtered_df = df[
        (df['Date'] >= selected_start_date) & 
        (df['Date'] <= selected_end_date) &
        (df['Primary Type'].isin(selected_crime_types)) &
        (df['Description'].isin(selected_descriptions))
    ]

    if not filtered_df.empty:
        st.write(filtered_df)
        st.header('Stats')
        st.metric(label="Number of Arrests", value=len(filtered_df))
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
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=filtered_df,
                    get_position='[lon, lat]',
                    get_color=[200, 30, 0, 160],
                    get_radius=100,
                ),
            ],
        ))
    else:
        st.warning("No data available for the selected criteria.")
