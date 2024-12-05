import pandas as pd
import pydeck as pdk
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import geopandas as gpd

# Path to the CSV file and GeoJSON file
csv_path = 'FastFoodRestaurants.csv'
geojson_path = 'us-states.json'
income_csv_path = 'Household_income.csv'

# Load the CSV data for fast food chains
df = pd.read_csv(csv_path)

# Filter out rows with duplicate (latitude, longitude) pairs and remove NA values
df_unique = df.drop_duplicates(subset=['latitude', 'longitude']).dropna()

# Group data by province (state) and count the number of rows (fast food chains) for each state
state_row_counts = df_unique.groupby('province').size().reset_index(name='row_count')

# Drop the row where the province is 'Co Spgs'
state_row_counts = state_row_counts[state_row_counts['province'] != 'Co Spgs']

# Define a mapping of state abbreviations to full names
state_abbreviation_to_name = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts',
    'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
    'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

# Map state abbreviations in 'province' column to full state names
state_row_counts['province'] = state_row_counts['province'].replace(state_abbreviation_to_name)

# Load the GeoJSON data for US states
with open(geojson_path) as f:
    us_states_geojson = json.load(f)

# Load the household income dataset
income_df = pd.read_csv(income_csv_path, encoding='ISO-8859-1')
income_df = income_df[['states', 'Mean income (dollars)']]  # Keep only relevant columns


# Merge GeoJSON with household income data
income_dict = dict(zip(income_df['states'], income_df['Mean income (dollars)']))
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    feature['properties']['income'] = income_dict.get(state_name, 0)  # Default income to 0 if not found



# Initialize to show the fast food map by default (Fast Food Chains visualization is selected by default)
show_household_income = "Household Income"


# Prepare the polygon layer
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    state_count = state_row_counts[state_row_counts['province'] == state_name]['row_count'].values
    feature['properties']['height'] = state_count[0] / 10 if len(state_count) > 0 else 0

# Create the polygon layer for household income with new income ranges from 0 to 130,000 in increments of 15,000
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    state_count = state_row_counts[state_row_counts['province'] == state_name]['row_count'].values
    feature['properties']['height'] = state_count[0] / 10 if len(state_count) > 0 else 0
    feature['properties']['height_n'] = feature['properties']['height']*10


    # Clean the income value by removing commas
    income = feature['properties']['income']
    income = str(income).replace(',', '')  # Remove commas
    income = int(income)  # Convert to integer after removing commas

    # Color based on household income with new ranges from 0 to 130,000 (increments of 15,000)
    if income <= 75000:
        color = [247, 251, 255, 255]  # Darker color for income 60,001–75,000
    elif income <= 90000:
        color = [224, 236, 244, 255]  # Even darker for income 75,001–90,000
    elif income <= 105000:
        color = [158, 188, 218, 255]  # Darker blue for income 90,001–105,000
    elif income <= 120000:
        color = [110, 1, 107, 255]  # Darker blue for income 105,001–120,000
    elif income <= 130000:
        color = [77, 0, 75, 255]  # Deep blue for income 120,001–130,000
    else:
        color = [42, 0, 72, 255]  # For income above 130,000, keep black (or adjust as needed)

    feature['properties']['color'] = color

    
# Create the polygon layer for visualization
polygon_layer = pdk.Layer(
    "GeoJsonLayer",
    us_states_geojson,
    pickable=True,
    stroked=False,
    filled=True,
    extruded=True,
    get_fill_color="properties.color",
    get_elevation="properties.height",
    elevation_scale=10000,
    wireframe=True,
)


# Set the initial view for the map
view_state = pdk.ViewState(
    longitude=-98.35, latitude=39.5, zoom=2.6,
    pitch=80,         
    bearing=-30
)

# Update the tooltip content based on the selected visualization
tooltip_content = """
<div style="background-color: #ffffcc; border-radius: 8px; padding: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); font-family: Arial, sans-serif; font-size: 12px;">
    <b>{name}</b><br/>
    {html_content}
</div>
"""
tooltip_html = (
    "Income: ${income}<br/>Density: {height_n}" 
)
tooltip = {
    "html": tooltip_content.replace("{html_content}", tooltip_html),
    "style": {
        "color": "black",
        "text-align": "center",
        "font-weight": "bold",
    },
}

# Render the Deck.gl visualization
deck = pdk.Deck(
    layers=[polygon_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style="mapbox://styles/mapbox/light-v10",
)

# Streamlit application
st.title("Life Plan Navigator A Data Visualization Journey")









# Sidebar navigation
st.sidebar.title("Navigator")

# Button handlers for each section
if st.sidebar.button("Food Locator"):
    st.session_state.selected_section = "Food Locator"
if st.sidebar.button("Best Place to Live"):
    st.session_state.selected_section = "Best Place to Live"
if st.sidebar.button("Smart Route Planner"):
    st.session_state.selected_section = "Smart Route Planner"


# Display content based on the selected section stored in session state
selected_section = getattr(st.session_state, "selected_section", "Food Locator")



if selected_section == "Food Locator":
    st.title("Food Locator")
    st.markdown(
        "<h2 style='font-size: 23px; font-weight: bold;'>Height - Food Outlet Density<br>Color gradient - Annual Household Income</h2>",
        unsafe_allow_html=True
    )

    # Display a legend for income visualization at the right corner (only for Household Income map)
    st.markdown(
        """
        <style>
            .legend {
                position: fixed;
                top: 50px;
                right: 50px;
                width: 180px;
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            }
            .legend div {
                margin: 5px 0;
            }
        </style>
        <div class="legend">
            <div style="background: rgba(247, 251, 255, 255); height: 20px; width: 20px; display: inline-block;"></div> 0–75,000<br>
            <div style="background: rgba(224, 236, 244, 255); height: 20px; width: 20px; display: inline-block;"></div> 75,001–90,000<br>
            <div style="background: rgba(158, 188, 218, 255); height: 20px; width: 20px; display: inline-block;"></div> 90,001–105,000<br>
            <div style="background: rgba(110, 1, 107, 255); height: 20px; width: 20px; display: inline-block;"></div> 105,001–120,000<br>
            <div style="background: rgba(77, 0, 75, 255); height: 20px; width: 20px; display: inline-block;"></div> 120,001–130,000<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render the map
    st.pydeck_chart(deck)
    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold;'>Food Locations Across California State</h2>",
        unsafe_allow_html=True
    )
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path)

    # File path to the dataset
    file_path = 'cal.csv'

    # Load data
    data = load_data(file_path)

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    # california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)
    california_map = folium.Map(location=[34.0522, -118.2437], zoom_start=11)

    # Add individual markers to the map
    for _, row in data.iterrows():
        tooltip_text = f"Name: {row['name']}<br>Address: {row['address']}"  # Combine name and address
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=tooltip_text,  # Popup to show details
            tooltip=tooltip_text  # Tooltip for hover
        ).add_to(california_map)

    # Display the map
    st_folium(california_map, width=800, height=600)

    
elif selected_section == "Best Place to Live":
    st.title("Best Place to Live")
    st.markdown(
        "<h2 style='font-size: 23px; font-weight: bold;'>Height - Food Outlet Density<br>Color gradient - Annual Household Income</h2>",
        unsafe_allow_html=True
    )
    # Display a legend for income visualization at the right corner (only for Household Income map)
    st.markdown(
        """
        <style>
            .legend {
                position: fixed;
                top: 50px;
                right: 50px;
                width: 180px;
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            }
            .legend div {
                margin: 5px 0;
            }
        </style>
        <div class="legend">
            <div style="background: rgba(247, 251, 255, 255); height: 20px; width: 20px; display: inline-block;"></div> 0–75,000<br>
            <div style="background: rgba(224, 236, 244, 255); height: 20px; width: 20px; display: inline-block;"></div> 75,001–90,000<br>
            <div style="background: rgba(158, 188, 218, 255); height: 20px; width: 20px; display: inline-block;"></div> 90,001–105,000<br>
            <div style="background: rgba(110, 1, 107, 255); height: 20px; width: 20px; display: inline-block;"></div> 105,001–120,000<br>
            <div style="background: rgba(77, 0, 75, 255); height: 20px; width: 20px; display: inline-block;"></div> 120,001–130,000<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render the map
    st.pydeck_chart(deck)
    st.markdown(
    "<h2 style='font-size: 28px; font-weight: bold;'>Food Locations Across California State</h2>",
    unsafe_allow_html=True
    )
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path)

    # File path to the dataset
    file_path = 'cal.csv'

    # Load data
    data = load_data(file_path)

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    # california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)
    california_map = folium.Map(location=[34.0522, -118.2437], zoom_start=11)

    # Add individual markers to the map
    for _, row in data.iterrows():
        tooltip_text = f"Name: {row['name']}<br>Address: {row['address']}"  # Combine name and address
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=tooltip_text,  # Popup to show details
            tooltip=tooltip_text  # Tooltip for hover
        ).add_to(california_map)

    # Display the map
    st_folium(california_map, width=800, height=600)


    # Code for Fitness centers and groceries
    # Load the CSV file
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path, encoding='ISO-8859-1')

    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold;'>Fitness Centers and Grocery Shops across Los Angeles</h2>",
        unsafe_allow_html=True
    )

    # File path to the dataset
    file_path = 'fitness_grocery.csv'

    # Load data
    data = load_data(file_path)
    data = data.dropna(subset=['latitude', 'Type'])  # Ensure 'Type' is not missing

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name", "Type"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    # california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)
    california_map = folium.Map(location=[34.0522, -118.2437], zoom_start=12)
    
    # Define a mapping for Types to icons and colors
    type_icon_mapping = {
        "fitness": {"icon": "heartbeat", "color": "red"},
        "grocery": {"icon": "shopping-cart", "color": "green"},
    }

    # Add individual markers to the map
    for _, row in data.iterrows():
        tooltip_text = f"Name: {row['name']}<br>Address: {row['address']}<br>Type: {row['Type']}"  # Include type info
        
        # Get the icon and color for the type
        icon_info = type_icon_mapping.get(row["Type"].lower(), {"icon": "info-sign", "color": "blue"})  # Default icon
        
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=tooltip_text,
            tooltip=tooltip_text,
            icon=folium.Icon(icon=icon_info["icon"], color=icon_info["color"])
        ).add_to(california_map)

    # Display the map
    st_folium(california_map, width=800, height=600)

elif selected_section == "Smart Route Planner":
    st.title("Smart Route Planner")
    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold;'>Food Locations Across California State</h2>",
        unsafe_allow_html=True
    )
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path)

    # File path to the dataset
    file_path = 'cal.csv'

    # Load data
    data = load_data(file_path)

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    # california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)
    california_map = folium.Map(location=[34.0522, -118.2437], zoom_start=11)

    # Add individual markers to the map
    for _, row in data.iterrows():
        tooltip_text = f"Name: {row['name']}<br>Address: {row['address']}"  # Combine name and address
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=tooltip_text,  # Popup to show details
            tooltip=tooltip_text  # Tooltip for hover
        ).add_to(california_map)

    # Display the map
    st_folium(california_map, width=800, height=600)


    # Code for Fitness centers and groceries
    # Load the CSV file
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path, encoding='ISO-8859-1')

    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold;'>Fitness Centers and Grocery Shops across Los Angeles</h2>",
        unsafe_allow_html=True
    )

    # File path to the dataset
    file_path = 'fitness_grocery.csv'

    # Load data
    data = load_data(file_path)
    data = data.dropna(subset=['latitude', 'Type'])  # Ensure 'Type' is not missing

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name", "Type"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    # california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)
    california_map = folium.Map(location=[34.0522, -118.2437], zoom_start=12)
    
    # Define a mapping for Types to icons and colors
    type_icon_mapping = {
        "fitness": {"icon": "heartbeat", "color": "red"},
        "grocery": {"icon": "shopping-cart", "color": "green"},
    }

    # Add individual markers to the map
    for _, row in data.iterrows():
        tooltip_text = f"Name: {row['name']}<br>Address: {row['address']}<br>Type: {row['Type']}"  # Include type info
        
        # Get the icon and color for the type
        icon_info = type_icon_mapping.get(row["Type"].lower(), {"icon": "info-sign", "color": "blue"})  # Default icon
        
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=tooltip_text,
            tooltip=tooltip_text,
            icon=folium.Icon(icon=icon_info["icon"], color=icon_info["color"])
        ).add_to(california_map)

    # Display the map
    st_folium(california_map, width=800, height=600)

    # Load the dataset
    df = pd.read_csv('us_commuting_modes.csv')

    # Load the GeoJSON data for US states
    geo_df = gpd.read_file('us-states.json')

    # Rename columns if necessary
    geo_df = geo_df.rename(columns={'name': 'State'})

    # Merge the GeoDataFrame with the dataset based on state name
    merged_df = geo_df.merge(df, on='State', how='left')


    # Display the dataset as a table in Streamlit
    st.header("USA Commute Modes Data")


    # Add a dropdown or radio button to select the commuting mode
    selected_mode = st.radio("Select a commuting mode to visualize:", ['Car', 'Bike', 'Public Transport', 'Walking'])

    # Set color schemes for each mode
    color_schemes = {
        'Car': 'Reds',
        'Bike': 'Blues',
        'Public Transport': 'Greens',
        'Walking': 'Purples'
    }

    # Determine the appropriate color scheme based on the selected mode
    color_scheme = color_schemes[selected_mode]

    # Create a Plotly map with the selected commuting mode
    fig = px.choropleth(
        merged_df,
        geojson=geo_df.geometry,
        locations=merged_df.index,
        color=f'{selected_mode} (%)',
        hover_name='State',
        hover_data=['Bike (%)', 'Car (%)', 'Public Transport (%)', 'Walking (%)'],
        title=f'US Commute Modes - {selected_mode} Commuting Percentage',
        color_continuous_scale=color_scheme,
        scope='usa'
    )

    # Update the map layout
    fig.update_geos(
        visible=True,
        projection_type="albers usa"
    )
    # st.dataframe(df)
    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)

else:
    # Default content if no section is selected
    st.title("Welcome")
    st.write("Use the sidebar to navigate to different sections.")
