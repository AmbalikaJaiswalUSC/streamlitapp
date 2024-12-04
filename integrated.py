import pandas as pd
import pydeck as pdk
import json
import streamlit as st
import folium
from streamlit_folium import st_folium

# Path to the CSV file and GeoJSON file
csv_path = r'D:\viterbi syllabus\dsci554\project_554\FastFoodRestaurants.csv'
geojson_path = r'D:\viterbi syllabus\dsci554\project_554\us-states.json'
income_csv_path = r'D:\viterbi syllabus\dsci554\project_554\Household_income.csv'
# death_csv_path = r'D:\viterbi syllabus\dsci554\project_554\Deaths_data.csv'
# # Creating DataFrame
obesity_csv_path = r'D:\viterbi syllabus\dsci554\project_554\obesity.csv'



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

# death_df = pd.read_csv(death_csv_path, encoding='ISO-8859-1')
# death_df = death_df[death_df['Year'] == 2017]
# death_df = death_df[['State', 'Cause Name', 'Deaths']]
# death_df = death_df[death_df['Cause Name'].isin(['Heart disease', 'Diabetes'])]
# death_df['Deaths'] = death_df['Deaths'].str.replace(',', '', regex=True).astype(int)
# result = death_df.groupby("State", as_index=False).agg({"Deaths": "sum"})
# result['Deaths'] = result['Deaths'].astype(str)

obesity_df = pd.read_csv(obesity_csv_path, encoding='ISO-8859-1')
# Grouping by 'LocationDesc' and calculating the average of 'Data_Value'
final_df = obesity_df.groupby('LocationDesc')['Data_Value'].mean().reset_index()

# Renaming columns for clarity
final_df.columns = ['State', 'Percent']
final_df['Percent'] = final_df['Percent'].round().astype(int)
final_df['Percent'] = final_df['Percent'].astype(str)

# Merge GeoJSON with household income data
income_dict = dict(zip(income_df['states'], income_df['Mean income (dollars)']))
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    feature['properties']['income'] = income_dict.get(state_name, 0)  # Default income to 0 if not found

# # Merge the death data into the GeoJSON data
# deaths_dict = dict(zip(result['State'], result['Deaths']))
# for feature in us_states_geojson['features']:
#     state_name = feature['properties']['name']
#     feature['properties']['deaths'] = deaths_dict.get(state_name, "0") 


obesity_dict = dict(zip(final_df['State'], final_df['Percent']))
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    feature['properties']['percent'] = obesity_dict.get(state_name, "0")


# Streamlit application
st.title("Welcome to Life Plan Navigator")

# # Show the "Household Income" radio button, which, when selected, switches to that visualization
# visualization_option = st.radio("Select Visualization", ["Household Income","Death Cases","Obesity cases"])

# Initialize to show the fast food map by default (Fast Food Chains visualization is selected by default)
show_household_income = "Household Income"
# show_death_cases = visualization_option == "Death Cases"
show_obesity_cases = "Obesity cases"

# Prepare the polygon layer
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    state_count = state_row_counts[state_row_counts['province'] == state_name]['row_count'].values
    feature['properties']['height'] = state_count[0] / 10 if len(state_count) > 0 else 0

# Create the polygon layer for household income with new income ranges from 0 to 130,000 in increments of 15,000
# Create the polygon layer for household income with new income ranges from 0 to 130,000 in increments of 15,000
for feature in us_states_geojson['features']:
    state_name = feature['properties']['name']
    state_count = state_row_counts[state_row_counts['province'] == state_name]['row_count'].values
    feature['properties']['height'] = state_count[0] / 10 if len(state_count) > 0 else 0
    feature['properties']['height_n'] = feature['properties']['height']*10


    

    if show_household_income:
        # Clean the income value by removing commas
        income = feature['properties']['income']
        income = str(income).replace(',', '')  # Remove commas
        income = int(income)  # Convert to integer after removing commas

        # Color based on household income with new ranges from 0 to 130,000 (increments of 15,000)
        # if income <= 15000:
        #     color = [247, 251, 255, 255]  # Light color for income 0–15,000
        # elif income <= 30000:
        #     color = [224, 236, 244, 255]  # Light-medium color for income 15,001–30,000
        # elif income <= 45000:
        #     color = [191, 211, 230, 255]  # Medium color for income 30,001–45,000
        # elif income <= 60000:
        #     color = [158, 188, 218, 255]  # Dark-medium color for income 45,001–60,000
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

    # elif show_death_cases:
    #         deaths=feature['properties']['deaths']
    #         deaths = int(deaths)  # Convert deaths to integer
            
    #         # Color based on deaths range
    #         # if deaths == '0':
    #         #     color = [255, 255, 255, 255]  # White for 0 deaths
    #         if deaths <= 1000:
    #             color = [255, 230, 230, 255]  # Light pink for 1–1,000 deaths
    #         elif deaths <= 5000:
    #             color = [255, 153, 153, 255]  # Medium pink for 1,001–5,000 deaths
    #         elif deaths <= 10000:
    #             color = [255, 51, 51, 255]  # Red for 5,001–10,000 deaths
    #         elif deaths <= 50000:
    #             color = [153, 0, 0, 255]  # Dark red for 10,001–50,000 deaths
    #         feature['properties']['color'] = color
    
    elif show_obesity_cases:
            percent=feature['properties']['percent']
            percent = int(percent) # Convert deaths to integer

            if  percent <= 25:
                color= [255, 255, 204, 255]  # Light yellow
            elif percent <= 30:
                color= [255, 255, 153, 255]  # Pale yellow
            elif percent <= 35:
                color= [255, 255, 102, 255]  # Medium yellow
            elif percent <= 40:
                color= [255, 255, 51, 255]   # Bright yellow
            else:
                color= [255, 204, 0, 255]    # Golden yellow
            feature['properties']['color'] = color


    else:
        # Default color for Fast Food Chains (no color change)
        feature['properties']['color'] = [255, 0, 0, 255]  # Red for Fast Food Chains
    


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

# Display a legend for income visualization at the right corner (only for Household Income map)
# if show_household_income:
#     st.markdown(
#         """
#         <style>
#             .legend {
#                 position: fixed;
#                 top: 50px;
#                 right: 50px;
#                 width: 180px;
#                 background: white;
#                 padding: 10px;
#                 border-radius: 5px;
#                 box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
#             }
#             .legend div {
#                 margin: 5px 0;
#             }
#         </style>
#         <div class="legend">
#             <div style="background: rgba(247, 251, 255, 255); height: 20px; width: 20px; display: inline-block;"></div> 0–75,000<br>
#             <div style="background: rgba(224, 236, 244, 255); height: 20px; width: 20px; display: inline-block;"></div> 75,001–90,000<br>
#             <div style="background: rgba(158, 188, 218, 255); height: 20px; width: 20px; display: inline-block;"></div> 90,001–105,000<br>
#             <div style="background: rgba(110, 1, 107, 255); height: 20px; width: 20px; display: inline-block;"></div> 105,001–120,000<br>
#             <div style="background: rgba(77, 0, 75, 255); height: 20px; width: 20px; display: inline-block;"></div> 120,001–130,000<br>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

# if show_death_cases:
#     st.markdown(
#         """
#         <style>
#             .legend {
#                 position: fixed;
#                 top: 50px;
#                 right: 50px;
#                 width: 180px;
#                 background: white;
#                 padding: 10px;
#                 border-radius: 5px;
#                 box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
#             }
#             .legend div {
#                 margin: 5px 0;
#             }
#         </style>
#         <div class="legend">
#             <div style="background: rgba(255, 230, 230, 255); height: 20px; width: 20px; display: inline-block;"></div> 1–1,000 deaths<br>
#             <div style="background: rgba(255, 153, 153, 255); height: 20px; width: 20px; display: inline-block;"></div> 1,001–5,000 deaths<br>
#             <div style="background: rgba(255, 51, 51, 255); height: 20px; width: 20px; display: inline-block;"></div> 5,001–10,000 deaths<br>
#             <div style="background: rgba(153, 0, 0, 255); height: 20px; width: 20px; display: inline-block;"></div> 10,001–50,000 deaths<br>
#             <div style="background: rgba(102, 0, 0, 255); height: 20px; width: 20px; display: inline-block;"></div> >50,000 deaths<br>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

# if show_obesity_cases:
    # st.markdown(
    #     """
    #     <style>
    #         .legend {
    #             position: fixed;
    #             top: 50px;
    #             right: 50px;
    #             width: 180px;
    #             background: white;
    #             padding: 10px;
    #             border-radius: 5px;
    #             box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
    #         }
    #         .legend div {
    #             margin: 5px 0;
    #         }
    #     </style>
    #     <div class="legend">
    #         <div style="background: rgba(255, 255, 204, 255); height: 20px; width: 20px; display: inline-block;"></div> 19–25%<br>
    #         <div style="background: rgba(255, 255, 153, 255); height: 20px; width: 20px; display: inline-block;"></div> 26–30%<br>
    #         <div style="background: rgba(255, 255, 102, 255); height: 20px; width: 20px; display: inline-block;"></div> 31–35%<br>
    #         <div style="background: rgba(255, 255, 51, 255); height: 20px; width: 20px; display: inline-block;"></div> 36–40%<br>
    #         <div style="background: rgba(255, 204, 0, 255); height: 20px; width: 20px; display: inline-block;"></div> >40%<br>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )

# Set the initial view for the map
view_state = pdk.ViewState(
    longitude=-98.35, latitude=39.5, zoom=4, pitch=45, bearing=0
)


# Update the tooltip content based on the selected visualization
tooltip_content = """
<div style="background-color: #ffffcc; border-radius: 8px; padding: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); font-family: Arial, sans-serif; font-size: 12px;">
    <b>{name}</b><br/>
    {html_content}
</div>
"""
tooltip_html = (
    # "Percent:{percent}<br/>Density: {height_n}" if show_obesity_cases else
    # "Deaths: {deaths}<br/>Density: {height_n}" if show_death_cases else
    "Income: ${income}<br/>Density: {height_n}" if show_household_income else
    "Density: {height_n}"
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

# Render the map
st.pydeck_chart(deck)

import streamlit as st

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
selected_section = getattr(st.session_state, "selected_section", None)

if selected_section == "Food Locator":
    st.markdown(
        """
        <style>
            .food-locator-title {
                background-color: #333; /* Dark background color */
                padding: 20px; /* Padding for spacing */
                border-radius: 8px; /* Rounded corners */
                color: white; /* White text color */
                text-align: center; /* Centered text */
            }
        </style>
        <div class="food-locator-title">
            <h1>Food Locator</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(
    "<h2 style='font-size: 28px; font-weight: bold;'>Food Locations Distribution Across the U.S</h2>",
    unsafe_allow_html=True
)
    
    

# Assume us_states_geojson is loaded with your GeoJSON data

# Step 1: Iterate through each feature and add the 'colors' property
    for feature in us_states_geojson['features']:
        percent = feature['properties']['percent']
        percent = int(percent)  # Convert percent to integer

        # Assign a color based on the 'percent' value
        if percent <= 25:
            color = [255, 255, 204, 255]  # Light yellow
        elif percent <= 30:
            color = [255, 255, 153, 255]  # Pale yellow
        elif percent <= 35:
            color = [255, 255, 102, 255]  # Medium yellow
        elif percent <= 40:
            color = [255, 255, 51, 255]   # Bright yellow
        else:
            color = [255, 204, 0, 255]    # Golden yellow

        # Add the color to the properties of the feature
        feature['properties']['colors'] = color

    # Step 2: Create the GeoJsonLayer and use the updated properties
    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        us_states_geojson,
        pickable=True,
        stroked=False,
        filled=True,
        extruded=True,
        get_fill_color="properties.colors",  # Reference the 'colors' property
        get_elevation="properties.height",
        elevation_scale=10000,
        wireframe=True,
    )

# You can now add polygon_layer to your deck.gl map


    
    view_state = pdk.ViewState(
           longitude=-98.35, latitude=39.5, zoom=4, pitch=45, bearing=0
    )


    # Update the tooltip content based on the selected visualization
    tooltip_content = """
    <div style="background-color: #ffffcc; border-radius: 8px; padding: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); font-family: Arial, sans-serif; font-size: 12px;">
        <b>{name}</b><br/>
        {html_content}
    </div>
    """
    tooltip_html = (
        "Percent:{percent}<br/>Density: {height_n}" if show_obesity_cases else
        "Density: {height_n}"
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
    st.pydeck_chart(deck)
    
    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold;'>Food Locations Across California State</h2>",
        unsafe_allow_html=True
    )
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path)

    # Main function to run the Streamlit app

  
    # st.write("Interactive map of California with data points from the provided file.")

    # File path to the dataset
    file_path = r"D:\viterbi syllabus\dsci554\project_554\cal.csv"

    # Load data
    data = load_data(file_path)

    # Validate necessary columns
    required_columns = ["latitude", "longitude", "address", "name"]
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    # Create a base map centered on California
    california_map = folium.Map(location=[37.5, -119.5], zoom_start=6)

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
    st.write("Explore the Best Place to Live section!")
elif selected_section == "Smart Route Planner":
    st.title("Smart Route Planner")
    st.write("Plan your routes in the Smart Route Planner section!")
else:
    # Default content if no section is selected
    st.title("Welcome")
    st.write("Use the sidebar to navigate to different sections.")
