import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Setting the title and sidebar options for city selection
st.title("NYC/Chicago Crime Visualization")
st.markdown("### Open the upper left corner sidebar to select city!")

# Function to load data with caching and error handling
@st.cache(allow_output_mutation=True)
def load_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

# Dictionary to map city names to file paths
dataframe_paths = {
    "Chicago Crime": "chicago.csv",
    "NYC Crime": "nyccrime.csv"
}

# Lazy loading of dataframes
@st.cache(allow_output_mutation=True)
def get_dataframes():
    return {city: load_dataframe(path) for city, path in dataframe_paths.items()}

# Load dataframes
dataframes = get_dataframes()

# Sidebar selection for cities
selected_cities = st.sidebar.multiselect("Select one City for Map", list(dataframe_paths.keys()))

# Main logic to process each selected city
for city in selected_cities:
    df = dataframes[city]
    if df.empty:
        continue  # Skip processing if the dataframe is empty

    # Setting latitude and longitude based on city
    latvalue, lonvalue = (41.81184357, -87.60681861) if city == "Chicago Crime" else (40.7569, -73.8757)

    # Handling date range selection
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

    # Crime type selection handling
    crime_types = df['Primary Type'].unique()
    selected_crime_types = st.sidebar.multiselect("Select crime types", options=crime_types, default=[])

    # Description selection based on selected crime types
    descriptions = df[df['Primary Type'].isin(selected_crime_types)]['Description'].unique()
    selected_descriptions = st.sidebar.multiselect("Select descriptions", options=descriptions, default=[])

    # Applying filters to the dataframe based on user selections
    filtered_df = df[
        (df['Date'] >= selected_start_date) & 
        (df['Date'] <= selected_end_date) &
        (df['Primary Type'].isin(selected_crime_types)) &
        (df['Description'].isin(selected_descriptions))
    ]

    # Display the filtered DataFrame
    st.write(filtered_df)

    # Display statistics and line chart
    st.header('Stats')
    st.metric(label="Number of Arrests", value=len(filtered_df))
    st.header('Line Chart', divider='gray')
    crime_counts_by_date = filtered_df.groupby(['Date', 'Primary Type']).size().unstack(fill_value=0)
    st.line_chart(crime_counts_by_date)

    # Map visualization with PyDeck
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
# Comment out the function calls when finished.
