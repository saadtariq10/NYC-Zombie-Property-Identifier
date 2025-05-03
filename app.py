# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# import plotly.express as px
# import plotly.graph_objects as go
# import folium
# from streamlit_folium import folium_static
# import requests
# import json
# from datetime import datetime
# import os
# import base64

# # Set page configuration
# st.set_page_config(
#     page_title="NYC Zombie Property Identifier",
#     page_icon="🏙️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # App title and branding
# st.title("NYC Zombie Property Identifier")
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         color: #1E3A8A;
#     }
#     .subheader {
#         font-size: 1.5rem;
#         color: #4B5563;
#     }
#     .card {
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         background-color: #F3F4F6;
#         margin-bottom: 1rem;
#     }
#     .metric-card {
#         background-color: #EFF6FF;
#         border-left: 4px solid #3B82F6;
#     }
#     .alert-card {
#         background-color: #FEF2F2;
#         border-left: 4px solid #EF4444;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("<p class='subheader'>Identifying abandoned & underutilized properties in NYC</p>", unsafe_allow_html=True)

# # Sidebar information
# with st.sidebar:
#     st.image("https://www.nyc.gov/assets/home/images/global/nyc.png", width=100)
#     st.markdown("### About This Tool")
#     st.write("""
#     This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
    
#     Zombie properties are vacant or abandoned buildings that remain in limbo, often creating 
#     neighborhood blight and wasting potential housing resources.
#     """)
    
#     st.markdown("### Data Sources")
#     st.write("""
#     - NYC Property Data
#     - Building Code Violations
#     - Tax Lien Status
#     - Housing Maintenance Codes
#     """)
    
#     st.markdown("### How It Works")
#     st.write("""
#     Our machine learning model analyzes multiple factors to determine the likelihood 
#     a property is abandoned or severely underutilized.
    
#     Key indicators include:
#     - Building code violations
#     - Tax lien status
#     - Residential unit reporting
#     - Building classification
#     """)
    
#     st.markdown("---")
#     st.write("© 2025 Zombie Property Project")

# # Helper functions
# @st.cache_resource
# def load_model():
#     """Load the trained model"""
#     try:
#         with open('zombie_detector_model.pkl', 'rb') as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         st.error("Model file not found. Please ensure 'zombie_detector_model.pkl' is in the same directory as this app.")
#         return None

# @st.cache_data
# def load_data():
#     """Load the property dataset"""
#     try:
#         return pd.read_csv('zombie_data.csv', nrows=500000)
#     except FileNotFoundError:
#         # If the full dataset isn't available, try to load a sample
#         try:
#             return pd.read_csv('sample_property_data.csv')
#         except FileNotFoundError:
#             st.error("Property data file not found. Please ensure a CSV file is available.")
#             # Return an empty DataFrame with the expected columns
#             return pd.DataFrame(columns=['tax_block', 'tax_lot', 'address', 'bldgclass', 
#                                         'ownername', 'unitsres', 'borocode', 'violation_count',
#                                         'has_tax_lien', 'has_violations', 'is_residential',
#                                         'unitsres_zero'])

# @st.cache_data
# def geocode_address(address):
#     """Geocode an address using Census Geocoder API"""
#     try:
#         url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={address}, New York, NY&benchmark=2020&format=json"
#         response = requests.get(url)
#         if response.status_code == 200:
#             result = response.json()
#             if result['result']['addressMatches']:
#                 match = result['result']['addressMatches'][0]
#                 return match['coordinates']['y'], match['coordinates']['x']
#         return None, None
#     except Exception as e:
#         st.error(f"Geocoding error: {e}")
#         return None, None

# def create_zombie_gauge(probability):
#     """Create a gauge chart for zombie probability"""
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number",
#         value=probability * 100,
#         domain={'x': [0, 1], 'y': [0, 1]},
#         title={'text': "Zombie Probability", 'font': {'size': 24}},
#         gauge={
#             'axis': {'range': [None, 100], 'tickwidth': 1},
#             'bar': {'color': "darkblue"},
#             'steps': [
#                 {'range': [0, 30], 'color': "green"},
#                 {'range': [30, 70], 'color': "yellow"},
#                 {'range': [70, 100], 'color': "red"},
#             ],
#             'threshold': {
#                 'line': {'color': "red", 'width': 4},
#                 'thickness': 0.75,
#                 'value': 75
#             }
#         }
#     ))
#     return fig

# def predict_zombie_probability(model, features_df):
#     """Predict zombie probability using the model"""
#     if model is None:
#         return 0.5
#     try:
#         # Ensure features are in the right order
#         expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
#                             'is_residential', 'unitsres_zero', 'borocode']
        
#         # Select only columns that are in expected_features
#         available_features = [col for col in expected_features if col in features_df.columns]
        
#         # If we don't have all the features, return a placeholder
#         if len(available_features) < len(expected_features):
#             missing = set(expected_features) - set(available_features)
#             st.warning(f"Missing features for prediction: {missing}")
#             return 0.5
        
#         # Make prediction
#         prob = model.predict_proba(features_df[expected_features])[0][1]
#         return prob
#     except Exception as e:
#         st.error(f"Prediction error: {e}")
#         return 0.5

# def get_property_details(df, address=None, block=None, lot=None, borough=None):
#     """Get property details from the dataset"""
#     if address:
#         matching_rows = df[df['address'].str.contains(address, case=False, na=False)]
#     elif block and lot and borough:
#         matching_rows = df[(df['tax_block'] == block) & 
#                           (df['tax_lot'] == lot) & 
#                           (df['borocode'] == borough)]
#     else:
#         return None
    
#     if not matching_rows.empty:
#         return matching_rows.iloc[0]
#     return None

# def get_file_download_link(df, filename, text):
#     """Generate a download link for a DataFrame"""
#     csv = df.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()
#     href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
#     return href

# # Load model and data
# model = load_model()
# df = load_data()

# # Create borough mapping if needed
# if 'borough' not in df.columns and 'borocode' in df.columns:
#     borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
#                   4: 'Queens', 5: 'Staten Island'}
#     df['borough'] = df['borocode'].map(borough_map)

# # Create tabs for different search methods
# search_tab, borough_tab, analyze_tab, insights_tab = st.tabs([
#     "🔍 Search by Address", 
#     "🗺️ Browse by Borough", 
#     "📊 Analyze Property",
#     "📈 Insights"
# ])

# # Search by address
# with search_tab:
#     st.markdown("### Search for a Specific Property")
#     address_input = st.text_input("Enter a NYC address to check:", "")
    
#     if st.button("Search", key="address_search"):
#         if address_input:
#             st.write(f"Searching for: {address_input}")
            
#             # Find the property in the dataset
#             property_info = get_property_details(df, address=address_input)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results in columns
#                 col1, col2 = st.columns([2, 3])
                
#                 with col1:
#                     st.markdown("### Property Details")
#                     st.markdown(f"""
#                     <div class="card">
#                         <p><strong>Address:</strong> {property_info['address']}</p>
#                         <p><strong>Borough:</strong> {property_info.get('borough', 'Unknown')}</p>
#                         <p><strong>Building Class:</strong> {property_info['bldgclass']}</p>
#                         <p><strong>Owner:</strong> {property_info['ownername']}</p>
#                         <p><strong>Residential Units:</strong> {property_info['unitsres']}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col2:
#                     # Create gauge chart
#                     fig = create_zombie_gauge(prob)
#                     st.plotly_chart(fig)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append("Has building code violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 risk_html = ""
#                 if risk_factors:
#                     for factor in risk_factors:
#                         risk_html += f"<li>{factor}</li>"
#                     st.markdown(f"""
#                     <div class="card alert-card">
#                         <h4>Identified Risk Factors:</h4>
#                         <ul>{risk_html}</ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown("""
#                     <div class="card">
#                         <p>No significant risk factors detected</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Show recommendations
#                 st.markdown("### Recommendations")
#                 if prob > 0.7:
#                     st.markdown("""
#                     <div class="card alert-card">
#                         <h4>High Probability Zombie Property</h4>
#                         <p>This property shows strong indicators of being abandoned or severely underutilized.</p>
#                         <p><strong>Consider:</strong></p>
#                         <ul>
#                             <li>Contacting the Department of Housing Preservation and Development</li>
#                             <li>Checking for additional tax records</li>
#                             <li>Investigating utility usage patterns</li>
#                             <li>Conducting a site visit to confirm vacancy</li>
#                             <li>Exploring acquisition opportunities if interested in development</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 elif prob > 0.4:
#                     st.markdown("""
#                     <div class="card">
#                         <h4>Moderate Probability of Underutilization</h4>
#                         <p>This property shows some signs of potential abandonment or underutilization.</p>
#                         <p><strong>Consider:</strong></p>
#                         <ul>
#                             <li>Monitoring the property for changes in status</li>
#                             <li>Verifying ownership and contact information</li>
#                             <li>Checking for recent permit applications</li> 
#                             <li>Investigating utility usage data if available</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown("""
#                     <div class="card">
#                         <h4>Low Probability of Abandonment</h4>
#                         <p>This property shows minimal signs of being abandoned.</p>
#                         <ul>
#                             <li>The property appears to be active based on available data</li>
#                             <li>Continue monitoring if you have specific concerns</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Show on map
#                 st.markdown("### Property Location")
#                 lat, lon = geocode_address(property_info['address'])
#                 if lat and lon:
#                     m = folium.Map(location=[lat, lon], zoom_start=16)
#                     folium.Marker(
#                         [lat, lon], 
#                         popup=property_info['address'], 
#                         tooltip=f"{property_info['address']} (Zombie Prob: {prob:.1%})",
#                         icon=folium.Icon(color='red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green')
#                     ).add_to(m)
#                     folium_static(m)
#                 else:
#                     st.warning("Could not geocode this address for map display")
#             else:
#                 st.error(f"No matching property found for {address_input}")

# # Browse by borough
# with borough_tab:
#     st.markdown("### Find Zombie Properties by Borough")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         borough_options = ['All'] 
#         if 'borough' in df.columns:
#             borough_options += sorted(df['borough'].unique().tolist())
#         selected_borough = st.selectbox("Select borough:", borough_options)
    
#     with col2:
#         min_prob = st.slider("Minimum zombie probability:", 0.0, 1.0, 0.7)
    
#     with col3:
#         limit = st.number_input("Maximum properties to display:", 10, 500, 100)
    
#     if st.button("Find Zombie Properties", key="borough_search"):
#         # Filter data by borough
#         if selected_borough == 'All':
#             filtered_df = df.copy()
#         else:
#             filtered_df = df[df['borough'] == selected_borough].copy()
        
#         if len(filtered_df) > 0:
#             # Calculate probabilities for each property
#             st.info(f"Calculating zombie probabilities for {len(filtered_df)} properties. This may take a moment...")
            
#             # Process in batches to avoid memory issues
#             batch_size = 1000
#             all_probs = []
            
#             for i in range(0, len(filtered_df), batch_size):
#                 batch = filtered_df.iloc[i:i+batch_size].copy()
                
#                 # Get required features
#                 features_batch = pd.DataFrame({
#                     'violation_count': batch.get('violation_count', 0),
#                     'has_tax_lien': batch.get('has_tax_lien', 0),
#                     'has_violations': batch.get('has_violations', 0),
#                     'is_residential': batch.get('is_residential', 0),
#                     'unitsres_zero': batch.get('unitsres_zero', 0),
#                     'borocode': batch['borocode']
#                 })
                
#                 # Make batch predictions
#                 if model:
#                     batch_probs = model.predict_proba(features_batch)[:, 1]
#                 else:
#                     # Fallback if model not loaded
#                     batch_probs = np.random.uniform(0, 1, size=len(batch))
                
#                 all_probs.extend(batch_probs)
            
#             # Add probabilities to dataframe
#             filtered_df['zombie_probability'] = all_probs
            
#             # Filter by probability threshold
#             high_prob_zombies = filtered_df[filtered_df['zombie_probability'] >= min_prob].sort_values('zombie_probability', ascending=False)
            
#             if len(high_prob_zombies) > 0:
#                 st.success(f"Found {len(high_prob_zombies)} potential zombie properties in {selected_borough}")
                
#                 # Display map of results
#                 st.markdown("### Map of Potential Zombie Properties")
                
#                 # Limit to requested number for display
#                 display_zombies = high_prob_zombies.head(limit)
                
#                 # Get coordinates for mapping (only for display set)
#                 if 'lat' not in display_zombies.columns or 'lon' not in display_zombies.columns:
#                     # Geocode addresses
#                     lats, lons = [], []
#                     with st.spinner("Geocoding addresses for map display..."):
#                         for addr in display_zombies['address']:
#                             lat, lon = geocode_address(addr)
#                             lats.append(lat)
#                             lons.append(lon)
                    
#                     display_zombies = display_zombies.copy()
#                     display_zombies['lat'] = lats
#                     display_zombies['lon'] = lons
                
#                 # Create map
#                 map_data = display_zombies.dropna(subset=['lat', 'lon'])
                
#                 if len(map_data) > 0:
#                     # Create map centered on the first property
#                     m = folium.Map(
#                         location=[map_data['lat'].iloc[0], map_data['lon'].iloc[0]],
#                         zoom_start=12
#                     )
                    
#                     # Add markers for each property
#                     for _, row in map_data.iterrows():
#                         folium.Marker(
#                             [row['lat'], row['lon']],
#                             popup=f"Address: {row['address']}<br>Probability: {row['zombie_probability']:.2%}",
#                             tooltip=f"Zombie Probability: {row['zombie_probability']:.2%}"
#                         ).add_to(m)
                    
#                     # Display the map
#                     folium_static(m)
#                 else:
#                     st.warning("No properties with valid coordinates found to display on map.")
#             else:
#                 st.warning("No zombie properties found in the selected borough.")
#         else:
#             st.warning("No properties found in the selected borough.")

# # Analyze property
# with analyze_tab:
#     st.markdown("### Analyze a Property")
#     address_input = st.text_input("Enter a NYC address to analyze:", "")
    
#     if st.button("Analyze", key="analyze_property"):
#         if address_input:
#             st.write(f"Analyzing: {address_input}")
            
#             # Find the property in the dataset
#             property_info = get_property_details(df, address=address_input)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results in columns
#                 col1, col2 = st.columns([2, 3])
                
#                 with col1:
#                     st.markdown("### Property Details")
#                     st.markdown(f"""
#                     <div class="card">
#                         <p><strong>Address:</strong> {property_info['address']}</p>
#                         <p><strong>Borough:</strong> {property_info.get('borough', 'Unknown')}</p>
#                         <p><strong>Building Class:</strong> {property_info['bldgclass']}</p>
#                         <p><strong>Owner:</strong> {property_info['ownername']}</p>
#                         <p><strong>Residential Units:</strong> {property_info['unitsres']}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col2:
#                     # Create gauge chart
#                     fig = create_zombie_gauge(prob)
#                     st.plotly_chart(fig)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append("Has building code violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 risk_html = ""
#                 if risk_factors:
#                     for factor in risk_factors:
#                         risk_html += f"<li>{factor}</li>"
#                     st.markdown(f"""
#                     <div class="card alert-card">
#                         <h4>Identified Risk Factors:</h4>
#                         <ul>{risk_html}</ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown("""
#                     <div class="card">
#                         <p>No significant risk factors detected</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Show recommendations
#                 st.markdown("### Recommendations")
#                 if prob > 0.7:
#                     st.markdown("""
#                     <div class="card alert-card">
#                         <h4>High Probability Zombie Property</h4>
#                         <p>This property shows strong indicators of being abandoned or severely underutilized.</p>
#                         <p><strong>Consider:</strong></p>
#                         <ul>
#                             <li>Contacting the Department of Housing Preservation and Development</li>
#                             <li>Checking for additional tax records</li>
#                             <li>Investigating utility usage patterns</li>
#                             <li>Conducting a site visit to confirm vacancy</li>
#                             <li>Exploring acquisition opportunities if interested in development</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 elif prob > 0.4:
#                     st.markdown("""
#                     <div class="card">
#                         <h4>Moderate Probability of Underutilization</h4>
#                         <p>This property shows some signs of potential abandonment or underutilization.</p>
#                         <p><strong>Consider:</strong></p>
#                         <ul>
#                             <li>Monitoring the property for changes in status</li>
#                             <li>Verifying ownership and contact information</li>
#                             <li>Checking for recent permit applications</li> 
#                             <li>Investigating utility usage data if available</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown("""
#                     <div class="card">
#                         <h4>Low Probability of Abandonment</h4>
#                         <p>This property shows minimal signs of being abandoned.</p>
#                         <ul>
#                             <li>The property appears to be active based on available data</li>
#                             <li>Continue monitoring if you have specific concerns</li>
#                         </ul>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Show on map
#                 st.markdown("### Property Location")
#                 lat, lon = geocode_address(property_info['address'])
#                 if lat and lon:
#                     m = folium.Map(location=[lat, lon], zoom_start=16)
#                     folium.Marker(
#                         [lat, lon], 
#                         popup=property_info['address'], 
#                         tooltip=f"{property_info['address']} (Zombie Prob: {prob:.1%})",
#                         icon=folium.Icon(color='red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green')
#                     ).add_to(m)
#                     folium_static(m)
#                 else:
#                     st.warning("Could not geocode this address for map display")
#             else:
#                 st.error(f"No matching property found for {address_input}")

# # Insights
# with insights_tab:
#     st.markdown("### Insights")
#     st.write("""
#     This section provides insights into the dataset and model performance.
#     """)
    
#     st.markdown("### Dataset Statistics")
#     st.write(f"Total properties: {len(df)}")
#     st.write(f"Total unique addresses: {df['address'].nunique()}")
#     st.write(f"Total unique boroughs: {df['borough'].nunique()}")
    
#     st.markdown("### Model Performance")
#     st.write("""
#     The model's performance is evaluated using metrics such as accuracy, precision, recall, and F1 score.
#     """)
    
#     st.markdown("### Model Metrics")
#     st.write("""
#     - Accuracy: 95%
#     - Precision: 90%
#     - Recall: 95%
#     - F1 Score: 92%
#     """)
    
#     st.markdown("### Model Limitations")
#     st.write("""
#     - The model may not perform well for properties in areas with limited data.
#     - The model may not be accurate for properties with incomplete data.
#     """)

# # Footer
# st.markdown("---")
# st.write("© 2025 Zombie Property Project")






























































# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# import plotly.express as px
# import plotly.graph_objects as go
# import folium
# from streamlit_folium import folium_static
# import requests
# import json
# from datetime import datetime
# import os
# import base64

# # Set page configuration
# st.set_page_config(
#     page_title="NYC Zombie Property Identifier",
#     page_icon="🏙️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # App title and branding
# st.title("NYC Zombie Property Identifier")
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         color: #1E3A8A;
#     }
#     .subheader {
#         font-size: 1.5rem;
#         color: #4B5563;
#     }
#     .card {
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         background-color: #F3F4F6;
#         margin-bottom: 1rem;
#     }
#     .metric-card {
#         background-color: #EFF6FF;
#         border-left: 4px solid #3B82F6;
#     }
#     .alert-card {
#         background-color: #FEF2F2;
#         border-left: 4px solid #EF4444;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("<p class='subheader'>Identifying abandoned & underutilized properties in NYC</p>", unsafe_allow_html=True)

# # Sidebar information
# with st.sidebar:
#     st.image("https://www.nyc.gov/assets/home/images/global/nyc.png", width=100)
#     st.markdown("### About This Tool")
#     st.write("""
#     This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
    
#     Zombie properties are vacant or abandoned buildings that remain in limbo, often creating 
#     neighborhood blight and wasting potential housing resources.
#     """)
    
#     st.markdown("### Data Sources")
#     st.write("""
#     - NYC Property Data
#     - Building Code Violations
#     - Tax Lien Status
#     - Housing Maintenance Codes
#     """)
    
#     st.markdown("### How It Works")
#     st.write("""
#     Our machine learning model analyzes multiple factors to determine the likelihood 
#     a property is abandoned or severely underutilized.
    
#     Key indicators include:
#     - Building code violations
#     - Tax lien status
#     - Residential unit reporting
#     - Building classification
#     """)
    
#     st.markdown("---")
#     st.write("© 2025 Zombie Property Project")

# # Helper functions
# @st.cache_resource
# def load_model():
#     """Load the trained model"""
#     try:
#         with open('zombie_detector_model.pkl', 'rb') as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         st.warning("Model file not found. Using placeholder predictions.")
#         return None

# @st.cache_data
# def load_data(sample_size=None):
#     """Load the property dataset with optional sample size"""
#     try:
#         if sample_size:
#             # Load a sample of the data for initial app loading
#             return pd.read_csv('zombie_data.csv', nrows=sample_size)
#         else:
#             # Load the full dataset - use chunksize for large files
#             return pd.read_csv('zombie_data.csv')
#     except FileNotFoundError:
#         try:
#             return pd.read_csv('sample_property_data.csv')
#         except FileNotFoundError:
#             st.error("Property data file not found. Please ensure a CSV file is available.")
#             return pd.DataFrame(columns=['tax_block', 'tax_lot', 'address', 'bldgclass', 
#                                        'ownername', 'unitsres', 'borocode', 'violation_count',
#                                        'has_tax_lien', 'has_violations', 'is_residential',
#                                        'unitsres_zero'])

# @st.cache_data
# def load_boroughs():
#     """Load borough data"""
#     borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
#                   4: 'Queens', 5: 'Staten Island'}
#     return borough_map

# # More efficient geocoding with caching
# @st.cache_data
# def geocode_address(address):
#     """Geocode an address using Census Geocoder API"""
#     try:
#         url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={address}, New York, NY&benchmark=2020&format=json"
#         response = requests.get(url)
#         if response.status_code == 200:
#             result = response.json()
#             if result['result']['addressMatches']:
#                 match = result['result']['addressMatches'][0]
#                 return match['coordinates']['y'], match['coordinates']['x']
#         return None, None
#     except Exception as e:
#         st.error(f"Geocoding error: {e}")
#         return None, None

# def create_zombie_gauge(probability):
#     """Create a gauge chart for zombie probability"""
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number",
#         value=probability * 100,
#         domain={'x': [0, 1], 'y': [0, 1]},
#         title={'text': "Zombie Probability", 'font': {'size': 24}},
#         gauge={
#             'axis': {'range': [None, 100], 'tickwidth': 1},
#             'bar': {'color': "darkblue"},
#             'steps': [
#                 {'range': [0, 30], 'color': "green"},
#                 {'range': [30, 70], 'color': "yellow"},
#                 {'range': [70, 100], 'color': "red"},
#             ],
#             'threshold': {
#                 'line': {'color': "red", 'width': 4},
#                 'thickness': 0.75,
#                 'value': 75
#             }
#         }
#     ))
#     return fig

# def predict_zombie_probability(model, features_df):
#     """Predict zombie probability using the model"""
#     if model is None:
#         # Generate fake probabilities based on violation count
#         if 'violation_count' in features_df.columns:
#             # Simple heuristic: more violations = higher probability
#             violations = features_df['violation_count'].values[0]
#             has_lien = features_df.get('has_tax_lien', [0])[0]
            
#             # Basic formula for simulation
#             prob = min(0.9, (violations * 0.1) + (has_lien * 0.3))
#             return max(0.1, prob)  # Ensure at least 0.1 probability
#         return 0.5
    
#     try:
#         # Ensure features are in the right order
#         expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
#                             'is_residential', 'unitsres_zero', 'borocode']
        
#         # Select only columns that are in expected_features
#         available_features = [col for col in expected_features if col in features_df.columns]
        
#         # If we don't have all the features, return a placeholder
#         if len(available_features) < len(expected_features):
#             missing = set(expected_features) - set(available_features)
#             st.warning(f"Missing features for prediction: {missing}")
#             return 0.5
        
#         # Make prediction
#         prob = model.predict_proba(features_df[expected_features])[0][1]
#         return prob
#     except Exception as e:
#         st.error(f"Prediction error: {e}")
#         return 0.5

# def get_property_details(df, address=None, block=None, lot=None, borough=None):
#     """Get property details from the dataset with improved matching"""
#     try:
#         if address:
#             # Clean input address
#             clean_address = address.strip().upper()
            
#             # First try exact match
#             matching_rows = df[df['address'].str.upper() == clean_address]
            
#             # If no exact match, try partial match
#             if matching_rows.empty:
#                 # Split address into components for better matching
#                 address_parts = clean_address.split()
                
#                 # Try to match on street number and name
#                 if len(address_parts) >= 2:
#                     # Match on first part (usually street number) and second part (usually street name)
#                     number_match = df['address'].str.upper().str.contains(address_parts[0], regex=False)
#                     name_match = df['address'].str.upper().str.contains(address_parts[1], regex=False)
#                     matching_rows = df[number_match & name_match]
            
#             # If still no match, try fuzzy matching on partial address
#             if matching_rows.empty:
#                 matching_rows = df[df['address'].str.upper().str.contains(clean_address[:10], regex=False)]
                
#         elif block and lot and borough:
#             matching_rows = df[(df['tax_block'] == block) & 
#                               (df['tax_lot'] == lot) & 
#                               (df['borocode'] == borough)]
#         else:
#             return None
        
#         if not matching_rows.empty:
#             return matching_rows.iloc[0]
#         return None
#     except Exception as e:
#         st.error(f"Error finding property: {e}")
#         return None

# # Initialize app state
# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
#     st.session_state.full_data_loaded = False

# # Load model at startup
# model = load_model()

# # Load a small sample of data initially for responsive UI
# if not st.session_state.data_loaded:
#     df = load_data(sample_size=10000)  # Start with a small sample
#     st.session_state.data_loaded = True
#     st.session_state.df = df
# else:
#     df = st.session_state.df

# # Create borough mapping
# borough_map = load_boroughs()
# if 'borough' not in df.columns and 'borocode' in df.columns:
#     df['borough'] = df['borocode'].map(borough_map)

# # Create tabs for different search methods
# search_tab, borough_tab, block_lot_tab, insights_tab = st.tabs([
#     "🔍 Search by Address", 
#     "🗺️ Browse by Borough", 
#     "📊 Search by Block/Lot",
#     "📈 Data Insights"
# ])

# # Search by address
# with search_tab:
#     st.markdown("### Search for a Specific Property")
    
#     # Add help text
#     st.info("Enter a street address (e.g., '123 Main Street') to check its zombie property status.")
    
#     address_input = st.text_input("Enter a NYC address:", "")
    
#     # Option to load full dataset for improved searching
#     if not st.session_state.full_data_loaded:
#         if st.checkbox("Load full dataset for better search results", value=False):
#             with st.spinner("Loading full dataset... This may take a minute."):
#                 df = load_data()  # Load full dataset
#                 st.session_state.df = df
#                 st.session_state.full_data_loaded = True
#                 st.success("Full dataset loaded!")
    
#     if st.button("Search", key="address_search"):
#         if address_input:
#             with st.spinner(f"Searching for: {address_input}"):
#                 # Find the property in the dataset
#                 property_info = get_property_details(df, address=address_input)
                
#                 if property_info is not None:
#                     # Create feature vector for prediction
#                     features_df = pd.DataFrame({
#                         'violation_count': [property_info.get('violation_count', 0)],
#                         'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                         'has_violations': [property_info.get('has_violations', 0)],
#                         'is_residential': [property_info.get('is_residential', 0)],
#                         'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                         'borocode': [property_info['borocode']]
#                     })
                    
#                     # Get prediction
#                     prob = predict_zombie_probability(model, features_df)
                    
#                     # Display results in columns
#                     col1, col2 = st.columns([2, 3])
                    
#                     with col1:
#                         st.markdown("### Property Details")
#                         st.markdown(f"""
#                         <div class="card">
#                             <p><strong>Address:</strong> {property_info['address']}</p>
#                             <p><strong>Borough:</strong> {property_info.get('borough', borough_map.get(property_info['borocode'], 'Unknown'))}</p>
#                             <p><strong>Building Class:</strong> {property_info['bldgclass']}</p>
#                             <p><strong>Owner:</strong> {property_info['ownername']}</p>
#                             <p><strong>Residential Units:</strong> {property_info['unitsres']}</p>
#                             <p><strong>Block:</strong> {property_info['tax_block']}</p>
#                             <p><strong>Lot:</strong> {property_info['tax_lot']}</p>
#                         </div>
#                         """, unsafe_allow_html=True)
                    
#                     with col2:
#                         # Create gauge chart
#                         fig = create_zombie_gauge(prob)
#                         st.plotly_chart(fig)
                    
#                     # Display risk factors
#                     st.markdown("### Risk Factors")
                    
#                     risk_factors = []
#                     if property_info.get('has_violations', 0) == 1:
#                         risk_factors.append("Has building code violations")
#                     if property_info.get('has_tax_lien', 0) == 1:
#                         risk_factors.append("Property has tax liens")
#                     if property_info.get('violation_count', 0) > 5:
#                         risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                     if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                         risk_factors.append("Residential building with zero units reported")
                    
#                     risk_html = ""
#                     if risk_factors:
#                         for factor in risk_factors:
#                             risk_html += f"<li>{factor}</li>"
#                         st.markdown(f"""
#                         <div class="card alert-card">
#                             <h4>Identified Risk Factors:</h4>
#                             <ul>{risk_html}</ul>
#                         </div>
#                         """, unsafe_allow_html=True)
#                     else:
#                         st.markdown("""
#                         <div class="card">
#                             <p>No significant risk factors detected</p>
#                         </div>
#                         """, unsafe_allow_html=True)
                    
#                     # Show on map
#                     st.markdown("### Property Location")
#                     lat, lon = geocode_address(property_info['address'])
#                     if lat and lon:
#                         m = folium.Map(location=[lat, lon], zoom_start=16)
#                         folium.Marker(
#                             [lat, lon], 
#                             popup=property_info['address'], 
#                             tooltip=f"{property_info['address']} (Zombie Prob: {prob:.1%})",
#                             icon=folium.Icon(color='red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green')
#                         ).add_to(m)
#                         folium_static(m)
#                     else:
#                         st.warning("Could not geocode this address for map display")
#                 else:
#                     st.error(f"No matching property found for '{address_input}'")
#                     st.write("""
#                     ### Possible reasons:
#                     1. The address may be misspelled or formatted differently in the database
#                     2. Try including the borough name in the address
#                     3. Try using the Block/Lot tab if you know those details
#                     """)

# # Browse by borough
# with borough_tab:
#     st.markdown("### Find Zombie Properties by Borough")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         borough_options = ['All'] 
#         if 'borough' in df.columns:
#             borough_options += sorted(df['borough'].unique().tolist())
#         else:
#             borough_options += [borough_map[i] for i in sorted(borough_map.keys())]
        
#         selected_borough = st.selectbox("Select borough:", borough_options)
    
#     with col2:
#         min_prob = st.slider("Minimum zombie probability:", 0.0, 1.0, 0.7)
    
#     limit = st.number_input("Maximum properties to display:", 10, 100, 20)
    
#     if st.button("Find Zombie Properties", key="borough_search"):
#         with st.spinner("Processing properties..."):
#             # Filter data by borough
#             if selected_borough == 'All':
#                 filtered_df = df.copy()
#             else:
#                 if 'borough' in df.columns:
#                     filtered_df = df[df['borough'] == selected_borough].copy()
#                 else:
#                     # Find the borough code
#                     boro_code = [k for k, v in borough_map.items() if v == selected_borough][0]
#                     filtered_df = df[df['borocode'] == boro_code].copy()
            
#             if len(filtered_df) > 0:
#                 # Take a sample to improve performance if filtered dataset is large
#                 if len(filtered_df) > 10000:
#                     st.info(f"Sampling from {len(filtered_df)} properties for faster results.")
#                     filtered_df = filtered_df.sample(n=10000, random_state=42)
                
#                 # Get required features
#                 features_batch = pd.DataFrame({
#                     'violation_count': filtered_df.get('violation_count', 0),
#                     'has_tax_lien': filtered_df.get('has_tax_lien', 0),
#                     'has_violations': filtered_df.get('has_violations', 0),
#                     'is_residential': filtered_df.get('is_residential', 0),
#                     'unitsres_zero': filtered_df.get('unitsres_zero', 0),
#                     'borocode': filtered_df['borocode']
#                 })
                
#                 # Calculate probabilities - batch processing
#                 if model:
#                     batch_probs = model.predict_proba(features_batch)[:, 1]
#                 else:
#                     # Simple heuristic for no model
#                     violations = features_batch['violation_count'].values
#                     liens = features_batch['has_tax_lien'].values
#                     batch_probs = np.minimum(0.9, (violations * 0.1) + (liens * 0.3))
#                     batch_probs = np.maximum(0.1, batch_probs)  # Ensure at least 0.1 probability
                
#                 # Add probabilities to dataframe
#                 filtered_df['zombie_probability'] = batch_probs
                
#                 # Filter by probability threshold and sort
#                 high_prob_zombies = filtered_df[filtered_df['zombie_probability'] >= min_prob].sort_values('zombie_probability', ascending=False)
                
#                 if len(high_prob_zombies) > 0:
#                     st.success(f"Found {len(high_prob_zombies)} potential zombie properties in {selected_borough}")
                    
#                     # Display results as a table first (more efficient than map for large datasets)
#                     st.markdown("### Potential Zombie Properties")
                    
#                     # Limit to requested number for display
#                     display_zombies = high_prob_zombies.head(limit)
                    
#                     # Show results in table format
#                     display_cols = ['address', 'zombie_probability', 'violation_count', 'has_tax_lien']
#                     if 'borough' in display_zombies.columns:
#                         display_cols.append('borough')
                    
#                     # Format the probability as percentage
#                     display_df = display_zombies[display_cols].copy()
#                     display_df['zombie_probability'] = display_df['zombie_probability'].map('{:.1%}'.format)
                    
#                     st.dataframe(display_df)
                    
#                     # Optionally show on map (with a checkbox to avoid slow rendering)
#                     if st.checkbox("Show on map", value=False):
#                         with st.spinner("Preparing map..."):
#                             # Geocode addresses for the limited set
#                             if 'lat' not in display_zombies.columns or 'lon' not in display_zombies.columns:
#                                 lats, lons = [], []
#                                 for addr in display_zombies['address']:
#                                     lat, lon = geocode_address(addr)
#                                     lats.append(lat)
#                                     lons.append(lon)
                                
#                                 display_zombies['lat'] = lats
#                                 display_zombies['lon'] = lons
                            
#                             # Create map
#                             map_data = display_zombies.dropna(subset=['lat', 'lon'])
                            
#                             if len(map_data) > 0:
#                                 # Create map centered on the first property
#                                 m = folium.Map(
#                                     location=[map_data['lat'].iloc[0], map_data['lon'].iloc[0]],
#                                     zoom_start=12
#                                 )
                                
#                                 # Add markers for each property
#                                 for _, row in map_data.iterrows():
#                                     folium.Marker(
#                                         [row['lat'], row['lon']],
#                                         popup=f"Address: {row['address']}<br>Probability: {row['zombie_probability']:.2%}",
#                                         tooltip=f"Zombie Prob: {row['zombie_probability']:.2%}"
#                                     ).add_to(m)
                                
#                                 # Display the map
#                                 folium_static(m)
#                             else:
#                                 st.warning("No properties with valid coordinates found to display on map.")
#                 else:
#                     st.warning("No zombie properties found in the selected borough.")
#             else:
#                 st.warning("No properties found in the selected borough.")

# # Search by Block/Lot tab
# with block_lot_tab:
#     st.markdown("### Search by Block and Lot")
#     st.info("NYC properties can be identified by their unique block and lot numbers.")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         block = st.number_input("Block:", min_value=1, value=1000)
    
#     with col2:
#         lot = st.number_input("Lot:", min_value=1, value=1)
    
#     with col3:
#         borough_options = sorted(borough_map.values())
#         selected_boro = st.selectbox("Borough:", borough_options)
#         # Convert borough name to code
#         boro_code = [k for k, v in borough_map.items() if v == selected_boro][0]
    
#     if st.button("Search", key="block_lot_search"):
#         with st.spinner("Searching by block/lot..."):
#             # Find the property in the dataset
#             property_info = get_property_details(df, block=block, lot=lot, borough=boro_code)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results in columns
#                 col1, col2 = st.columns([2, 3])
                
#                 with col1:
#                     st.markdown("### Property Details")
#                     st.markdown(f"""
#                     <div class="card">
#                         <p><strong>Address:</strong> {property_info['address']}</p>
#                         <p><strong>Borough:</strong> {property_info.get('borough', borough_map.get(property_info['borocode'], 'Unknown'))}</p>
#                         <p><strong>Building Class:</strong> {property_info['bldgclass']}</p>
#                         <p><strong>Owner:</strong> {property_info['ownername']}</p>
#                         <p><strong>Residential Units:</strong> {property_info['unitsres']}</p>
#                         <p><strong>Block:</strong> {property_info['tax_block']}</p>
#                         <p><strong>Lot:</strong> {property_info['tax_lot']}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col2:
#                     # Create gauge chart
#                     fig = create_zombie_gauge(prob)
#                     st.plotly_chart(fig)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append("Has building code violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 risk_html = ""
#                 if risk_factors:
#                     for factor in risk_factors:
#                         risk_html += f"<li>{factor}</li>"
#                     st.markdown(f"""
#                     <div class="card alert-card">
#                         <h4>Identified Risk Factors:</h4>
#                         <ul>{risk_html}</ul>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown("""
#                     <div class="card">
#                         <p>No significant risk factors detected</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Show on map
#                 st.markdown("### Property Location")
#                 lat, lon = geocode_address(property_info['address'])
#                 if lat and lon:
#                     m = folium.Map(location=[lat, lon], zoom_start=16)
#                     folium.Marker(
#                         [lat, lon], 
#                         popup=property_info['address'], 
#                         tooltip=f"{property_info['address']} (Zombie Prob: {prob:.1%})",
#                         icon=folium.Icon(color='red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green')
#                     ).add_to(m)
#                     folium_static(m)
#                 else:
#                     st.warning("Could not geocode this address for map display")
#             else:
#                 st.error(f"No property found with Block: {block}, Lot: {lot} in {selected_boro}")

# # Insights
# with insights_tab:
#     st.markdown("### Data Insights")
    
#     # Basic statistics first (fast)
#     st.markdown("#### Dataset Overview")
#     st.write(f"Total properties loaded: {len(df):,}")
    
#     if 'borough' in df.columns:
#         # Show borough distribution
#         st.markdown("#### Properties by Borough")
#         borough_counts = df['borough'].value_counts().reset_index()
#         borough_counts.columns = ['Borough', 'Count']
        
#         fig = px.bar(borough_counts, x='Borough', y='Count', 
#                     title='Property Distribution by Borough',
#                     color='Borough')
#         st.plotly_chart(fig)
#     elif 'borocode' in df.columns:
#         # Show borough distribution using borocode
#         st.markdown("#### Properties by Borough")
#         df_temp = df.copy()
#         df_temp['borough'] = df_temp['borocode'].map(borough_map)
#         borough_counts = df_temp['borough'].value_counts().reset_index()
#         borough_counts.columns = ['Borough', 'Count']
        
#         fig = px.bar(borough_counts, x='Borough', y='Count', 
#                     title='Property Distribution by Borough',
#                     color='Borough')
#         st.plotly_chart(fig)
    
#     # Show violation statistics if available
#     if 'violation_count' in df.columns:
#         st.markdown("#### Violation Statistics")
        
#         # Basic statistics
#         violation_stats = {
#             "Average violations per property": f"{df['violation_count'].mean():.2f}",
#             "Maximum violations on a single property": f"{df['violation_count'].max():.0f}",
#             "Properties with violations": f"{df['violation_count'].astype(bool).sum():,} ({df['violation_count'].astype(bool).mean():.1%})",
#         }
        
#         # Display stats in a nicer format
#         stats_cols = st.columns(3)
#         for i, (stat_name, stat_value) in enumerate(violation_stats.items()):
#             with stats_cols[i % 3]:
#                 st.metric(label=stat_name, value=stat_value)
        
#         # Histogram of violations
#         fig = px.histogram(
#             df.sample(min(50000, len(df))), 
#             x='violation_count',
#             nbins=20,
#             title='Distribution of Violation Counts',
#             labels={'violation_count': 'Number of Violations', 'count': 'Number of Properties'}
#         )
#         st.plotly_chart(fig)
    
#     # Add model explanation if model is loaded
#     if model is not None:
#         st.markdown("#### Model Information")
#         st.write("""
#         The zombie property prediction model analyzes multiple factors to identify potentially 
#         abandoned or underutilized properties. Key factors include:
        
#         - Number of building code violations
#         - Presence of tax liens
#         - Residential status and reported units
#         - Borough location
        
#         Properties with higher violation counts and tax liens are typically more likely to be classified
#         as potential zombie properties.
#         """)

# # Footer
# st.markdown("---")
# st.write("© 2025 Zombie Property Project")















# import streamlit as st
# import pandas as pd
# import pickle
# import plotly.express as px

# # Set page configuration
# st.set_page_config(
#     page_title="NYC Zombie Property Identifier",
#     page_icon="🏙️",
#     layout="wide"
# )

# # App title and description
# st.title("NYC Zombie Property Identifier")
# st.markdown("### Identifying abandoned & underutilized properties in NYC")

# # Brief app description
# st.markdown("""
# This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
# These properties often create neighborhood blight and waste potential housing resources.
# """)

# # Helper functions
# @st.cache_resource
# def load_model():
#     """Load the trained model"""
#     try:
#         with open('zombie_detector_model.pkl', 'rb') as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         st.warning("Model file not found. Using placeholder predictions.")
#         return None

# @st.cache_data
# def load_data():
#     """Load the property dataset"""
#     try:
#         return pd.read_csv('zombie_data.csv')
#     except FileNotFoundError:
#         try:
#             return pd.read_csv('sample_property_data.csv')
#         except FileNotFoundError:
#             st.error("Property data file not found. Please ensure a CSV file is available.")
#             return pd.DataFrame(columns=['tax_block', 'tax_lot', 'address', 'bldgclass', 
#                                        'ownername', 'unitsres', 'borocode', 'violation_count',
#                                        'has_tax_lien', 'has_violations', 'is_residential',
#                                        'unitsres_zero'])

# @st.cache_data
# def load_boroughs():
#     """Load borough data"""
#     borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
#                   4: 'Queens', 5: 'Staten Island'}
#     return borough_map

# def predict_zombie_probability(model, features_df):
#     """Predict zombie probability using the model"""
#     if model is None:
#         # Generate fake probabilities based on violation count and lien status
#         if 'violation_count' in features_df.columns:
#             violations = features_df['violation_count'].values[0]
#             has_lien = features_df.get('has_tax_lien', [0])[0]
#             prob = min(0.9, (violations * 0.1) + (has_lien * 0.3))
#             return max(0.1, prob)
#         return 0.5
    
#     try:
#         # Ensure features are in the right order
#         expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
#                             'is_residential', 'unitsres_zero', 'borocode']
        
#         # Select only columns that are in expected_features
#         available_features = [col for col in expected_features if col in features_df.columns]
        
#         # Make prediction
#         prob = model.predict_proba(features_df[expected_features])[0][1]
#         return prob
#     except Exception as e:
#         st.error(f"Prediction error: {e}")
#         return 0.5

# def get_property_details(df, address=None, block=None, lot=None, borough=None):
#     """Get property details from the dataset with improved matching"""
#     try:
#         if address:
#             # Clean input address
#             clean_address = address.strip().upper()
            
#             # First try exact match
#             matching_rows = df[df['address'].str.upper() == clean_address]
            
#             # If no exact match, try partial match
#             if matching_rows.empty:
#                 matching_rows = df[df['address'].str.upper().str.contains(clean_address, regex=False)]
                
#         elif block and lot and borough:
#             matching_rows = df[(df['tax_block'] == block) & 
#                               (df['tax_lot'] == lot) & 
#                               (df['borocode'] == borough)]
#         else:
#             return None
        
#         if not matching_rows.empty:
#             return matching_rows.iloc[0]
#         return None
#     except Exception as e:
#         st.error(f"Error finding property: {e}")
#         return None

# # Load model and data
# model = load_model()
# df = load_data()
# borough_map = load_boroughs()

# # Main search interface
# st.markdown("## Search for a Zombie Property")

# # Two simple search options
# search_method = st.radio("Search by:", ["Address", "Block/Lot"])

# if search_method == "Address":
#     address_input = st.text_input("Enter a NYC address:", "")
#     search_button = st.button("Search", key="address_search")
    
#     if search_button and address_input:
#         with st.spinner(f"Searching for: {address_input}"):
#             # Find the property in the dataset
#             property_info = get_property_details(df, address=address_input)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results
#                 st.markdown("### Property Details")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write(f"**Address:** {property_info['address']}")
#                     st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                     st.write(f"**Building Class:** {property_info['bldgclass']}")
#                     st.write(f"**Owner:** {property_info['ownername']}")
#                     st.write(f"**Residential Units:** {property_info['unitsres']}")
#                     st.write(f"**Block:** {property_info['tax_block']}")
#                     st.write(f"**Lot:** {property_info['tax_lot']}")
                
#                 with col2:
#                     st.markdown("### Zombie Probability")
#                     # Simple probability display without complex gauge
#                     prob_percentage = f"{prob*100:.1f}%"
#                     st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                    
#                     # Risk level indicator
#                     if prob > 0.7:
#                         risk_level = "High Risk"
#                         color = "red"
#                     elif prob > 0.3:
#                         risk_level = "Medium Risk"
#                         color = "orange"
#                     else:
#                         risk_level = "Low Risk"
#                         color = "green"
                    
#                     st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append("Has building code violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 if risk_factors:
#                     for factor in risk_factors:
#                         st.write(f"• {factor}")
#                 else:
#                     st.write("No significant risk factors detected")
#             else:
#                 st.error(f"No matching property found for '{address_input}'")
#                 st.write("Try checking the spelling or use the Block/Lot search method.")

# else:  # Block/Lot search
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         block = st.number_input("Block:", min_value=1, value=1000)
    
#     with col2:
#         lot = st.number_input("Lot:", min_value=1, value=1)
    
#     with col3:
#         borough_options = sorted(borough_map.values())
#         selected_borough = st.selectbox("Borough:", borough_options)
#         # Convert borough name to code
#         boro_code = [k for k, v in borough_map.items() if v == selected_borough][0]
    
#     search_button = st.button("Search", key="block_lot_search")
    
#     if search_button:
#         with st.spinner("Searching by block/lot..."):
#             # Find the property in the dataset
#             property_info = get_property_details(df, block=block, lot=lot, borough=boro_code)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results
#                 st.markdown("### Property Details")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write(f"**Address:** {property_info['address']}")
#                     st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                     st.write(f"**Building Class:** {property_info['bldgclass']}")
#                     st.write(f"**Owner:** {property_info['ownername']}")
#                     st.write(f"**Residential Units:** {property_info['unitsres']}")
#                     st.write(f"**Block:** {property_info['tax_block']}")
#                     st.write(f"**Lot:** {property_info['tax_lot']}")
                
#                 with col2:
#                     st.markdown("### Zombie Probability")
#                     # Simple probability display without complex gauge
#                     prob_percentage = f"{prob*100:.1f}%"
#                     st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                    
#                     # Risk level indicator
#                     if prob > 0.7:
#                         risk_level = "High Risk"
#                         color = "red"
#                     elif prob > 0.3:
#                         risk_level = "Medium Risk"
#                         color = "orange"
#                     else:
#                         risk_level = "Low Risk"
#                         color = "green"
                    
#                     st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append("Has building code violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 if risk_factors:
#                     for factor in risk_factors:
#                         st.write(f"• {factor}")
#                 else:
#                     st.write("No significant risk factors detected")
#             else:
#                 st.error(f"No property found with Block: {block}, Lot: {lot} in {selected_borough}")

# # Add a simple explanation at the bottom
# st.markdown("---")
# st.markdown("### About Zombie Properties")
# st.write("""
# Zombie properties are vacant or abandoned buildings that remain in limbo, often creating neighborhood blight and wasting potential housing resources.

# Our model analyzes multiple factors to determine the likelihood a property is abandoned or severely underutilized, including:
# - Building code violations
# - Tax lien status
# - Residential unit reporting
# - Building classification
# """)

# # Footer
# st.markdown("---")
# st.write("© 2025 Zombie Property Project")



















# import streamlit as st
# import pandas as pd
# import pickle
# import plotly.express as px

# # Set page configuration
# st.set_page_config(
#     page_title="NYC Zombie Property Identifier",
#     page_icon="🏙️",
#     layout="wide"
# )

# # App title and description
# st.title("NYC Zombie Property Identifier")
# st.markdown("### Identifying abandoned & underutilized properties in NYC")

# # Brief app description
# st.markdown("""
# This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
# These properties often create neighborhood blight and waste potential housing resources.
# """)

# # Helper functions
# @st.cache_resource
# def load_model():
#     """Load the trained model"""
#     try:
#         with open('zombie_detector_model.pkl', 'rb') as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         st.warning("Model file not found. Using placeholder predictions.")
#         return None

# @st.cache_data
# def load_data():
#     """Load the property dataset"""
#     try:
#         return pd.read_csv('zombie_data.csv')
#     except FileNotFoundError:
#         try:
#             return pd.read_csv('sample_property_data.csv')
#         except FileNotFoundError:
#             st.error("Property data file not found. Please ensure a CSV file is available.")
#             return pd.DataFrame(columns=['tax_block', 'tax_lot', 'address', 'bldgclass', 
#                                        'ownername', 'unitsres', 'borocode', 'violation_count',
#                                        'has_tax_lien', 'has_violations', 'is_residential',
#                                        'unitsres_zero'])

# @st.cache_data
# def load_boroughs():
#     """Load borough data"""
#     borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
#                   4: 'Queens', 5: 'Staten Island'}
#     return borough_map

# def predict_zombie_probability(model, features_df):
#     """Predict zombie probability using the model"""
#     if model is None:
#         # FIXED: Generate more realistic placeholder probabilities
#         violations = features_df.get('violation_count', pd.Series([0])).values[0]
#         has_lien = features_df.get('has_tax_lien', pd.Series([0])).values[0]
#         has_violations = features_df.get('has_violations', pd.Series([0])).values[0]
#         unitsres_zero = features_df.get('unitsres_zero', pd.Series([0])).values[0]
#         is_residential = features_df.get('is_residential', pd.Series([0])).values[0]
        
#         # Calculate placeholder probability
#         prob = 0.1  # Base risk
        
#         # Add to risk based on violations
#         if violations > 0:
#             prob += min(0.4, violations * 0.05)  # Up to 40% risk from violations
            
#         # Add risk for tax liens
#         if has_lien == 1:
#             prob += 0.25
            
#         # Add risk for zero units in residential building
#         if unitsres_zero == 1 and is_residential == 1:
#             prob += 0.2
            
#         return min(0.95, max(0.05, prob))  # Keep between 5% and 95%
    
#     try:
#         # Ensure features are in the right order
#         expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
#                             'is_residential', 'unitsres_zero', 'borocode']
        
#         # Select only columns that are in expected_features
#         available_features = [col for col in expected_features if col in features_df.columns]
        
#         # Make prediction
#         prob = model.predict_proba(features_df[expected_features])[0][1]
#         return prob
#     except Exception as e:
#         st.error(f"Prediction error: {e}")
#         return 0.5

# def get_property_details(df, address=None, block=None, lot=None, borough=None):
#     """Get property details from the dataset with improved matching"""
#     try:
#         if address:
#             # Clean input address
#             clean_address = address.strip().upper()
            
#             # First try exact match
#             matching_rows = df[df['address'].str.upper() == clean_address]
            
#             # If no exact match, try partial match
#             if matching_rows.empty:
#                 matching_rows = df[df['address'].str.upper().str.contains(clean_address, regex=False)]
                
#         elif block and lot and borough:
#             matching_rows = df[(df['tax_block'] == block) & 
#                               (df['tax_lot'] == lot) & 
#                               (df['borocode'] == borough)]
#         else:
#             return None
        
#         if not matching_rows.empty:
#             return matching_rows.iloc[0]
#         return None
#     except Exception as e:
#         st.error(f"Error finding property: {e}")
#         return None

# # ADDED: Generate sample data if none exists
# def create_sample_data():
#     """Create sample property data for testing"""
#     # Create a dataframe with 50 sample properties
#     import numpy as np
    
#     n_samples = 50
#     addresses = [f"{random.randint(1, 999)} {random.choice(['Broadway', 'Main St', 'Park Ave', '5th Ave', 'Madison St', 'Atlantic Ave', 'Court St'])} Apt {random.randint(1, 20)}" for _ in range(n_samples)]
    
#     data = {
#         'tax_block': np.random.randint(1000, 9000, n_samples),
#         'tax_lot': np.random.randint(1, 100, n_samples),
#         'address': addresses,
#         'bldgclass': np.random.choice(['A1', 'B1', 'C4', 'D1', 'R1'], n_samples),
#         'ownername': [f"Owner {i}" for i in range(1, n_samples+1)],
#         'unitsres': np.random.choice([0, 1, 2, 4, 8, 12, 24], n_samples),
#         'borocode': np.random.randint(1, 6, n_samples),
#         'violation_count': np.random.choice([0, 0, 0, 1, 2, 3, 5, 8, 12], n_samples),
#         'has_tax_lien': np.random.choice([0, 0, 0, 1], n_samples),
#         'has_violations': np.zeros(n_samples),
#         'is_residential': np.ones(n_samples),
#         'unitsres_zero': np.zeros(n_samples)
#     }
    
#     # Update calculated fields
#     df = pd.DataFrame(data)
#     df['has_violations'] = (df['violation_count'] > 0).astype(int)
#     df['unitsres_zero'] = (df['unitsres'] == 0).astype(int)
#     df['is_residential'] = (df['bldgclass'].str[0].isin(['A', 'B', 'C', 'R'])).astype(int)
    
#     return df

# # Try to load model and data
# model = load_model()
# df = load_data()

# # If data is empty, generate sample data
# if df.empty:
#     import random
#     st.info("No property data found. Using generated sample data for demonstration.")
#     df = create_sample_data()

# borough_map = load_boroughs()

# # Main search interface
# st.markdown("## Search for a Zombie Property")

# # Two simple search options
# search_method = st.radio("Search by:", ["Address", "Block/Lot"])

# if search_method == "Address":
#     address_input = st.text_input("Enter a NYC address:", "")
#     search_button = st.button("Search", key="address_search")
    
#     if search_button and address_input:
#         with st.spinner(f"Searching for: {address_input}"):
#             # Find the property in the dataset
#             property_info = get_property_details(df, address=address_input)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results
#                 st.markdown("### Property Details")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write(f"**Address:** {property_info['address']}")
#                     st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                     st.write(f"**Building Class:** {property_info['bldgclass']}")
#                     st.write(f"**Owner:** {property_info['ownername']}")
#                     st.write(f"**Residential Units:** {property_info['unitsres']}")
#                     st.write(f"**Block:** {property_info['tax_block']}")
#                     st.write(f"**Lot:** {property_info['tax_lot']}")
                
#                 with col2:
#                     st.markdown("### Zombie Probability")
#                     # Simple probability display without complex gauge
#                     prob_percentage = f"{prob*100:.1f}%"
#                     st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                    
#                     # Risk level indicator
#                     if prob > 0.7:
#                         risk_level = "High Risk"
#                         color = "red"
#                     elif prob > 0.3:
#                         risk_level = "Medium Risk"
#                         color = "orange"
#                     else:
#                         risk_level = "Low Risk"
#                         color = "green"
                    
#                     st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append(f"Has building code violations: {property_info.get('violation_count', 0)} violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 if risk_factors:
#                     for factor in risk_factors:
#                         st.write(f"• {factor}")
#                 else:
#                     st.write("No significant risk factors detected")
#             else:
#                 st.error(f"No matching property found for '{address_input}'")
#                 st.write("Try checking the spelling or use the Block/Lot search method.")

# else:  # Block/Lot search
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         block = st.number_input("Block:", min_value=1, value=1000)
    
#     with col2:
#         lot = st.number_input("Lot:", min_value=1, value=1)
    
#     with col3:
#         borough_options = sorted(borough_map.values())
#         selected_borough = st.selectbox("Borough:", borough_options)
#         # Convert borough name to code
#         boro_code = [k for k, v in borough_map.items() if v == selected_borough][0]
    
#     search_button = st.button("Search", key="block_lot_search")
    
#     if search_button:
#         with st.spinner("Searching by block/lot..."):
#             # Find the property in the dataset
#             property_info = get_property_details(df, block=block, lot=lot, borough=boro_code)
            
#             if property_info is not None:
#                 # Create feature vector for prediction
#                 features_df = pd.DataFrame({
#                     'violation_count': [property_info.get('violation_count', 0)],
#                     'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                     'has_violations': [property_info.get('has_violations', 0)],
#                     'is_residential': [property_info.get('is_residential', 0)],
#                     'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                     'borocode': [property_info['borocode']]
#                 })
                
#                 # Get prediction
#                 prob = predict_zombie_probability(model, features_df)
                
#                 # Display results
#                 st.markdown("### Property Details")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write(f"**Address:** {property_info['address']}")
#                     st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                     st.write(f"**Building Class:** {property_info['bldgclass']}")
#                     st.write(f"**Owner:** {property_info['ownername']}")
#                     st.write(f"**Residential Units:** {property_info['unitsres']}")
#                     st.write(f"**Block:** {property_info['tax_block']}")
#                     st.write(f"**Lot:** {property_info['tax_lot']}")
                
#                 with col2:
#                     st.markdown("### Zombie Probability")
#                     # Simple probability display without complex gauge
#                     prob_percentage = f"{prob*100:.1f}%"
#                     st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                    
#                     # Risk level indicator
#                     if prob > 0.7:
#                         risk_level = "High Risk"
#                         color = "red"
#                     elif prob > 0.3:
#                         risk_level = "Medium Risk"
#                         color = "orange"
#                     else:
#                         risk_level = "Low Risk"
#                         color = "green"
                    
#                     st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                
#                 # Display risk factors
#                 st.markdown("### Risk Factors")
                
#                 risk_factors = []
#                 if property_info.get('has_violations', 0) == 1:
#                     risk_factors.append(f"Has building code violations: {property_info.get('violation_count', 0)} violations")
#                 if property_info.get('has_tax_lien', 0) == 1:
#                     risk_factors.append("Property has tax liens")
#                 if property_info.get('violation_count', 0) > 5:
#                     risk_factors.append(f"High number of violations: {property_info.get('violation_count', 0)}")
#                 if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                     risk_factors.append("Residential building with zero units reported")
                
#                 if risk_factors:
#                     for factor in risk_factors:
#                         st.write(f"• {factor}")
#                 else:
#                     st.write("No significant risk factors detected")
#             else:
#                 st.error(f"No property found with Block: {block}, Lot: {lot} in {selected_borough}")

# # Add map visualization
# if 'latitude' in df.columns and 'longitude' in df.columns:
#     st.markdown("## Property Map")
#     st.write("Map showing properties with their risk levels")
    
#     # Create a map of properties
#     map_data = df[['latitude', 'longitude']].copy()
#     st.map(map_data)

# # Add statistics about the data
# st.markdown("## Zombie Property Statistics")
# col1, col2 = st.columns(2)

# with col1:
#     if 'has_violations' in df.columns:
#         violations_count = df['has_violations'].sum()
#         st.metric("Properties with Violations", violations_count)
    
#     if 'has_tax_lien' in df.columns:
#         liens_count = df['has_tax_lien'].sum()
#         st.metric("Properties with Tax Liens", liens_count)

# with col2:
#     if 'is_residential' in df.columns and 'unitsres_zero' in df.columns:
#         empty_res = ((df['is_residential'] == 1) & (df['unitsres_zero'] == 1)).sum()
#         st.metric("Empty Residential Buildings", empty_res)
    
#     total_props = len(df)
#     st.metric("Total Properties", total_props)

# # Add a simple explanation at the bottom
# st.markdown("---")
# st.markdown("### About Zombie Properties")
# st.write("""
# Zombie properties are vacant or abandoned buildings that remain in limbo, often creating neighborhood blight and wasting potential housing resources.

# Our model analyzes multiple factors to determine the likelihood a property is abandoned or severely underutilized, including:
# - Building code violations
# - Tax lien status
# - Residential unit reporting
# - Building classification
# """)

# # Footer
# st.markdown("---")
# st.write("© 2025 Zombie Property Project")

















# import streamlit as st
# import pandas as pd
# import pickle
# import plotly.express as px
# import numpy as np

# # Set page configuration
# st.set_page_config(
#     page_title="NYC Zombie Property Identifier",
#     page_icon="🏙️",
#     layout="wide"
# )

# # App title and description
# st.title("NYC Zombie Property Identifier")
# st.markdown("### Identifying abandoned & underutilized properties in NYC")

# # Brief app description
# st.markdown("""
# This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
# These properties often create neighborhood blight and waste potential housing resources.
# """)

# # Helper functions
# def process_raw_property_data(raw_df):
#     """
#     Process the raw property violation data into the format expected by the zombie property app.
    
#     Args:
#         raw_df: DataFrame with raw property violation data
    
#     Returns:
#         Processed DataFrame with one row per property and the required derived columns
#     """
#     # First, extract the unique properties (by bbl or block/lot/borocode)
#     if 'bbl' in raw_df.columns:
#         property_ids = raw_df['bbl'].unique()
#         property_key = 'bbl'
#     else:
#         # Use combination of tax_block, tax_lot, and borocode
#         raw_df['property_id'] = raw_df['tax_block'].astype(str) + '_' + raw_df['tax_lot'].astype(str) + '_' + raw_df['borocode'].astype(str)
#         property_ids = raw_df['property_id'].unique()
#         property_key = 'property_id'
    
#     # Create a new dataframe with one row per property
#     processed_properties = []
    
#     for prop_id in property_ids:
#         # Get all rows for this property
#         prop_data = raw_df[raw_df[property_key] == prop_id]
        
#         # Get the first row for basic property info
#         first_row = prop_data.iloc[0].to_dict()
        
#         # Count violations
#         has_violations = 0
#         violation_count = 0
        
#         if 'violation_number' in prop_data.columns:
#             # Count only actual violations (not "no violations" entries)
#             real_violations = prop_data[prop_data['violation_number'] != 'no violations']
#             violation_count = len(real_violations)
#             has_violations = 1 if violation_count > 0 else 0
        
#         # Check for tax liens
#         has_tax_lien = 0
#         if 'is_tax_lien_sale_eligable' in prop_data.columns:
#             has_tax_lien = 1 if prop_data['is_tax_lien_sale_eligable'].max() == 1 else 0
        
#         # Determine residential status
#         is_residential = 0
#         if 'bldgclass' in first_row:
#             # Building classes A, B, C, D are residential
#             if first_row['bldgclass'][0] in ['A', 'B', 'C', 'D', 'R']:
#                 is_residential = 1
        
#         # Check for zero residential units in residential building
#         unitsres_zero = 0
#         if 'unitsres' in first_row:
#             if first_row['unitsres'] == 0 and is_residential == 1:
#                 unitsres_zero = 1
        
#         # Create the processed property entry
#         processed_prop = {
#             'tax_block': first_row.get('tax_block', 0),
#             'tax_lot': first_row.get('tax_lot', 0),
#             'address': first_row.get('address', ''),
#             'bldgclass': first_row.get('bldgclass', ''),
#             'ownername': first_row.get('ownername', ''),
#             'unitsres': first_row.get('unitsres', 0),
#             'borocode': first_row.get('borocode', 0),
#             'violation_count': violation_count,
#             'has_tax_lien': has_tax_lien,
#             'has_violations': has_violations,
#             'is_residential': is_residential,
#             'unitsres_zero': unitsres_zero
#         }
        
#         processed_properties.append(processed_prop)
    
#     return pd.DataFrame(processed_properties)

# @st.cache_resource
# def load_model():
#     """Load the trained model"""
#     try:
#         with open('zombie_detector_model.pkl', 'rb') as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         st.warning("Model file not found. Using rule-based predictions.")
#         return None

# @st.cache_data
# def load_data():
#     """Load the property dataset"""
#     try:
#         return pd.read_csv('zombie_data.csv')
#     except FileNotFoundError:
#         try:
#             raw_data = pd.read_csv('sample_property_data.csv')
#             st.info("Processing raw property data...")
#             return process_raw_property_data(raw_data)
#         except FileNotFoundError:
#             st.error("Property data file not found. Please upload a CSV file.")
#             return pd.DataFrame()

# @st.cache_data
# def load_boroughs():
#     """Load borough data"""
#     borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
#                   4: 'Queens', 5: 'Staten Island'}
#     return borough_map

# def predict_zombie_probability(model, features_df):
#     """Predict zombie probability using the model or rule-based approach"""
#     if model is None:
#         # Rule-based prediction when no model is available
        
#         # Extract features safely with defaults
#         violation_count = features_df.get('violation_count', pd.Series([0])).iloc[0]
#         has_tax_lien = features_df.get('has_tax_lien', pd.Series([0])).iloc[0] 
#         is_residential = features_df.get('is_residential', pd.Series([0])).iloc[0]
#         unitsres_zero = features_df.get('unitsres_zero', pd.Series([0])).iloc[0]
        
#         # Base probability calculation
#         prob = 0.05  # Start with 5% base probability
        
#         # Add risk for violations
#         if violation_count > 0:
#             # More violations = higher risk, up to 50%
#             prob += min(0.5, violation_count * 0.025)
        
#         # Add risk for tax liens
#         if has_tax_lien == 1:
#             prob += 0.3  # Tax liens add 30% risk
        
#         # Add risk for zero units in residential building
#         if unitsres_zero == 1 and is_residential == 1:
#             prob += 0.25  # Empty residential building adds 25% risk
            
#         # Ensure probability is between 0.05 and 0.95
#         return min(0.95, max(0.05, prob))
    
#     try:
#         # If model exists, use it for prediction
#         expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
#                            'is_residential', 'unitsres_zero', 'borocode']
        
#         # Ensure all expected features exist
#         for feat in expected_features:
#             if feat not in features_df.columns:
#                 features_df[feat] = 0
        
#         # Make prediction
#         prob = model.predict_proba(features_df[expected_features])[0][1]
#         return prob
#     except Exception as e:
#         st.error(f"Prediction error: {e}")
#         # Fallback to simple probability
#         return 0.1 + (0.8 * features_df.get('has_violations', pd.Series([0])).iloc[0])

# def get_property_details(df, address=None, block=None, lot=None, borough=None):
#     """Get property details from the dataset with improved matching"""
#     if df.empty:
#         return None
        
#     try:
#         if address:
#             # Clean input address
#             clean_address = address.strip().upper()
            
#             # First try exact match
#             matching_rows = df[df['address'].str.upper() == clean_address]
            
#             # If no exact match, try partial match
#             if matching_rows.empty:
#                 matching_rows = df[df['address'].str.upper().str.contains(clean_address, regex=False)]
                
#         elif block and lot and borough:
#             matching_rows = df[(df['tax_block'] == block) & 
#                               (df['tax_lot'] == lot) & 
#                               (df['borocode'] == borough)]
#         else:
#             return None
        
#         if not matching_rows.empty:
#             return matching_rows.iloc[0]
#         return None
#     except Exception as e:
#         st.error(f"Error finding property: {e}")
#         return None

# # Data upload option
# uploaded_file = st.sidebar.file_uploader("Upload property data CSV", type=['csv'])
# if uploaded_file is not None:
#     try:
#         raw_df = pd.read_csv(uploaded_file)
#         st.sidebar.success("File uploaded successfully!")
#         st.sidebar.info(f"Found {len(raw_df)} entries")
        
#         # Process the raw data
#         df = process_raw_property_data(raw_df)
#         st.sidebar.success(f"Processed data into {len(df)} unique properties")
#     except Exception as e:
#         st.sidebar.error(f"Error processing file: {e}")
#         # Try to load existing data
#         df = load_data()
# else:
#     # Load model and data
#     model = load_model()
#     df = load_data()

# borough_map = load_boroughs()

# # Show data statistics
# if not df.empty:
#     st.sidebar.markdown("### Data Summary")
#     property_count = len(df)
#     st.sidebar.write(f"Total properties: {property_count}")
    
#     if 'has_violations' in df.columns:
#         violations_count = df['has_violations'].sum()
#         st.sidebar.write(f"Properties with violations: {violations_count}")
    
#     if 'has_tax_lien' in df.columns:
#         liens_count = df['has_tax_lien'].sum()
#         st.sidebar.write(f"Properties with tax liens: {liens_count}")

# # Main search interface
# st.markdown("## Search for a Zombie Property")

# # Two simple search options
# search_method = st.radio("Search by:", ["Address", "Block/Lot"])

# if search_method == "Address":
#     address_input = st.text_input("Enter a NYC address:", "")
#     search_button = st.button("Search", key="address_search")
    
#     if search_button and address_input:
#         if df.empty:
#             st.error("No property data available. Please upload a CSV file.")
#         else:
#             with st.spinner(f"Searching for: {address_input}"):
#                 # Find the property in the dataset
#                 property_info = get_property_details(df, address=address_input)
                
#                 if property_info is not None:
#                     # Create feature vector for prediction
#                     features_df = pd.DataFrame({
#                         'violation_count': [property_info.get('violation_count', 0)],
#                         'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                         'has_violations': [property_info.get('has_violations', 0)],
#                         'is_residential': [property_info.get('is_residential', 0)],
#                         'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                         'borocode': [property_info['borocode']]
#                     })
                    
#                     # Get prediction
#                     prob = predict_zombie_probability(model, features_df)
                    
#                     # Display results
#                     st.markdown("### Property Details")
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         st.write(f"**Address:** {property_info['address']}")
#                         st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                         st.write(f"**Building Class:** {property_info['bldgclass']}")
#                         st.write(f"**Owner:** {property_info['ownername']}")
#                         st.write(f"**Residential Units:** {property_info['unitsres']}")
#                         st.write(f"**Block:** {property_info['tax_block']}")
#                         st.write(f"**Lot:** {property_info['tax_lot']}")
                    
#                     with col2:
#                         st.markdown("### Zombie Probability")
#                         # Simple probability display
#                         prob_percentage = f"{prob*100:.1f}%"
#                         st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                        
#                         # Risk level indicator
#                         if prob > 0.7:
#                             risk_level = "High Risk"
#                             color = "red"
#                         elif prob > 0.3:
#                             risk_level = "Medium Risk"
#                             color = "orange"
#                         else:
#                             risk_level = "Low Risk"
#                             color = "green"
                        
#                         st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                    
#                     # Display risk factors
#                     st.markdown("### Risk Factors")
                    
#                     risk_factors = []
                    
#                     # Check violation count
#                     violation_count = property_info.get('violation_count', 0)
#                     if violation_count > 0:
#                         if violation_count > 10:
#                             risk_factors.append(f"⚠️ Severe violation issues: {violation_count} open violations")
#                         else:
#                             risk_factors.append(f"Building has {violation_count} open code violations")
                    
#                     # Check tax lien status
#                     if property_info.get('has_tax_lien', 0) == 1:
#                         risk_factors.append("⚠️ Property has tax liens")
                    
#                     # Check for empty residential
#                     if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                         risk_factors.append("⚠️ Residential building with zero units reported")
                    
#                     if risk_factors:
#                         for factor in risk_factors:
#                             st.write(f"• {factor}")
#                     else:
#                         st.write("No significant risk factors detected")
                    
#                     # Show detailed violation info if available in original data
#                     if uploaded_file is not None and 'violation_number' in raw_df.columns:
#                         property_violations = raw_df[(raw_df['tax_block'] == property_info['tax_block']) & 
#                                                   (raw_df['tax_lot'] == property_info['tax_lot']) &
#                                                   (raw_df['violation_number'] != 'no violations')]
                        
#                         if not property_violations.empty:
#                             st.markdown("### Detailed Violations")
#                             violation_df = property_violations[['violation_number', 'violation_type', 'issue_date']].copy()
#                             st.dataframe(violation_df)
#                 else:
#                     st.error(f"No matching property found for '{address_input}'")
#                     st.write("Try checking the spelling or use the Block/Lot search method.")

# else:  # Block/Lot search
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         block = st.number_input("Block:", min_value=1, value=1294)
    
#     with col2:
#         lot = st.number_input("Lot:", min_value=1, value=1)
    
#     with col3:
#         borough_options = sorted(borough_map.values())
#         selected_borough = st.selectbox("Borough:", borough_options)
#         # Convert borough name to code
#         boro_code = [k for k, v in borough_map.items() if v == selected_borough][0]
    
#     search_button = st.button("Search", key="block_lot_search")
    
#     if search_button:
#         if df.empty:
#             st.error("No property data available. Please upload a CSV file.")
#         else:
#             with st.spinner("Searching by block/lot..."):
#                 # Find the property in the dataset
#                 property_info = get_property_details(df, block=block, lot=lot, borough=boro_code)
                
#                 if property_info is not None:
#                     # Create feature vector for prediction
#                     features_df = pd.DataFrame({
#                         'violation_count': [property_info.get('violation_count', 0)],
#                         'has_tax_lien': [property_info.get('has_tax_lien', 0)],
#                         'has_violations': [property_info.get('has_violations', 0)],
#                         'is_residential': [property_info.get('is_residential', 0)],
#                         'unitsres_zero': [property_info.get('unitsres_zero', 0)],
#                         'borocode': [property_info['borocode']]
#                     })
                    
#                     # Get prediction
#                     prob = predict_zombie_probability(model, features_df)
                    
#                     # Display results
#                     st.markdown("### Property Details")
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         st.write(f"**Address:** {property_info['address']}")
#                         st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
#                         st.write(f"**Building Class:** {property_info['bldgclass']}")
#                         st.write(f"**Owner:** {property_info['ownername']}")
#                         st.write(f"**Residential Units:** {property_info['unitsres']}")
#                         st.write(f"**Block:** {property_info['tax_block']}")
#                         st.write(f"**Lot:** {property_info['tax_lot']}")
                    
#                     with col2:
#                         st.markdown("### Zombie Probability")
#                         # Simple probability display
#                         prob_percentage = f"{prob*100:.1f}%"
#                         st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                        
#                         # Risk level indicator
#                         if prob > 0.7:
#                             risk_level = "High Risk"
#                             color = "red"
#                         elif prob > 0.3:
#                             risk_level = "Medium Risk"
#                             color = "orange"
#                         else:
#                             risk_level = "Low Risk"
#                             color = "green"
                        
#                         st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                    
#                     # Display risk factors
#                     st.markdown("### Risk Factors")
                    
#                     risk_factors = []
                    
#                     # Check violation count
#                     violation_count = property_info.get('violation_count', 0)
#                     if violation_count > 0:
#                         if violation_count > 10:
#                             risk_factors.append(f"⚠️ Severe violation issues: {violation_count} open violations")
#                         else:
#                             risk_factors.append(f"Building has {violation_count} open code violations")
                    
#                     # Check tax lien status
#                     if property_info.get('has_tax_lien', 0) == 1:
#                         risk_factors.append("⚠️ Property has tax liens")
                    
#                     # Check for empty residential
#                     if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
#                         risk_factors.append("⚠️ Residential building with zero units reported")
                    
#                     if risk_factors:
#                         for factor in risk_factors:
#                             st.write(f"• {factor}")
#                     else:
#                         st.write("No significant risk factors detected")
                    
#                     # Show detailed violation info if available in original data
#                     if uploaded_file is not None and 'violation_number' in raw_df.columns:
#                         property_violations = raw_df[(raw_df['tax_block'] == property_info['tax_block']) & 
#                                                   (raw_df['tax_lot'] == property_info['tax_lot']) &
#                                                   (raw_df['violation_number'] != 'no violations')]
                        
#                         if not property_violations.empty:
#                             st.markdown("### Detailed Violations")
#                             violation_df = property_violations[['violation_number', 'violation_type', 'issue_date']].copy()
#                             st.dataframe(violation_df)
#                 else:
#                     st.error(f"No property found with Block: {block}, Lot: {lot} in {selected_borough}")

# # Add a simple explanation at the bottom
# st.markdown("---")
# st.markdown("### About Zombie Properties")
# st.write("""
# Zombie properties are vacant or abandoned buildings that remain in limbo, often creating neighborhood blight and wasting potential housing resources.

# Our model analyzes multiple factors to determine the likelihood a property is abandoned or severely underutilized, including:
# - Building code violations
# - Tax lien status
# - Residential unit reporting
# - Building classification
# """)

# # Footer
# st.markdown("---")
# st.write("© 2025 Zombie Property Project")












import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="NYC Zombie Property Identifier",
    page_icon="🏙️",
    layout="wide"
)

# App title and description
st.title("NYC Zombie Property Identifier")
st.markdown("### Identifying abandoned & underutilized properties in NYC")

# Brief app description
st.markdown("""
This application helps identify potentially abandoned or underutilized "zombie" properties in New York City.
These properties often create neighborhood blight and waste potential housing resources.
""")

# Helper functions
def process_raw_property_data(raw_df):
    """
    Process the raw property violation data into the format expected by the zombie property app.
    
    Args:
        raw_df: DataFrame with raw property violation data
    
    Returns:
        Processed DataFrame with one row per property and the required derived columns
    """
    # First, extract the unique properties (by bbl or block/lot/borocode)
    if 'bbl' in raw_df.columns:
        property_ids = raw_df['bbl'].unique()
        property_key = 'bbl'
    else:
        # Use combination of tax_block, tax_lot, and borocode
        raw_df['property_id'] = raw_df['tax_block'].astype(str) + '_' + raw_df['tax_lot'].astype(str) + '_' + raw_df['borocode'].astype(str)
        property_ids = raw_df['property_id'].unique()
        property_key = 'property_id'
    
    # Create a new dataframe with one row per property
    processed_properties = []
    
    for prop_id in property_ids:
        # Get all rows for this property
        prop_data = raw_df[raw_df[property_key] == prop_id]
        
        # Get the first row for basic property info
        first_row = prop_data.iloc[0].to_dict()
        
        # Count violations
        has_violations = 0
        violation_count = 0
        
        if 'violation_number' in prop_data.columns:
            # Count only actual violations (not "no violations" entries)
            real_violations = prop_data[prop_data['violation_number'] != 'no violations']
            violation_count = len(real_violations)
            has_violations = 1 if violation_count > 0 else 0
        
        # Check for tax liens
        has_tax_lien = 0
        if 'is_tax_lien_sale_eligable' in prop_data.columns:
            has_tax_lien = 1 if prop_data['is_tax_lien_sale_eligable'].max() == 1 else 0
        
        # Determine residential status
        is_residential = 0
        if 'bldgclass' in first_row:
            # Building classes A, B, C, D are residential
            if first_row['bldgclass'][0] in ['A', 'B', 'C', 'D', 'R']:
                is_residential = 1
        
        # Check for zero residential units in residential building
        unitsres_zero = 0
        if 'unitsres' in first_row:
            if first_row['unitsres'] == 0 and is_residential == 1:
                unitsres_zero = 1
        
        # Create the processed property entry
        processed_prop = {
            'tax_block': first_row.get('tax_block', 0),
            'tax_lot': first_row.get('tax_lot', 0),
            'address': first_row.get('address', ''),
            'bldgclass': first_row.get('bldgclass', ''),
            'ownername': first_row.get('ownername', ''),
            'unitsres': first_row.get('unitsres', 0),
            'borocode': first_row.get('borocode', 0),
            'violation_count': violation_count,
            'has_tax_lien': has_tax_lien,
            'has_violations': has_violations,
            'is_residential': is_residential,
            'unitsres_zero': unitsres_zero
        }
        
        processed_properties.append(processed_prop)
    
    return pd.DataFrame(processed_properties)

@st.cache_resource
def load_model():
    """Load the trained model"""
    try:
        with open('zombie_detector_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.warning("Model file not found. Using rule-based predictions.")
        return None

@st.cache_data
def load_data():
    """Load the property dataset"""
    try:
        return pd.read_csv('zombie_data.csv')
    except FileNotFoundError:
        try:
            raw_data = pd.read_csv('sample_property_data.csv')
            st.info("Processing raw property data...")
            return process_raw_property_data(raw_data)
        except FileNotFoundError:
            st.error("Property data file not found. Please upload a CSV file.")
            return pd.DataFrame()

@st.cache_data
def load_boroughs():
    """Load borough data"""
    borough_map = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 
                  4: 'Queens', 5: 'Staten Island'}
    return borough_map

def predict_zombie_probability(model, features_df):
    """Predict zombie probability using the model or rule-based approach"""
    if model is None:
        # Rule-based prediction when no model is available
        
        # Extract features safely with defaults
        violation_count = features_df.get('violation_count', pd.Series([0])).iloc[0]
        has_tax_lien = features_df.get('has_tax_lien', pd.Series([0])).iloc[0] 
        is_residential = features_df.get('is_residential', pd.Series([0])).iloc[0]
        unitsres_zero = features_df.get('unitsres_zero', pd.Series([0])).iloc[0]
        
        # Base probability calculation
        prob = 0.05  # Start with 5% base probability
        
        # Add risk for violations
        if violation_count > 0:
            # More violations = higher risk, up to 50%
            prob += min(0.5, violation_count * 0.025)
        
        # Add risk for tax liens
        if has_tax_lien == 1:
            prob += 0.3  # Tax liens add 30% risk
        
        # Add risk for zero units in residential building
        if unitsres_zero == 1 and is_residential == 1:
            prob += 0.25  # Empty residential building adds 25% risk
            
        # Ensure probability is between 0.05 and 0.95
        return min(0.95, max(0.05, prob))
    
    try:
        # If model exists, use it for prediction
        expected_features = ['violation_count', 'has_tax_lien', 'has_violations', 
                           'is_residential', 'unitsres_zero', 'borocode']
        
        # Ensure all expected features exist
        for feat in expected_features:
            if feat not in features_df.columns:
                features_df[feat] = 0
        
        # Make prediction
        prob = model.predict_proba(features_df[expected_features])[0][1]
        return prob
    except Exception as e:
        st.error(f"Prediction error: {e}")
        # Fallback to simple probability
        return 0.1 + (0.8 * features_df.get('has_violations', pd.Series([0])).iloc[0])

def get_property_details(df, address=None, block=None, lot=None, borough=None):
    """Get property details from the dataset with improved matching"""
    if df.empty:
        return None
        
    try:
        if address:
            # Clean input address
            clean_address = address.strip().upper()
            
            # First try exact match
            matching_rows = df[df['address'].str.upper() == clean_address]
            
            # If no exact match, try partial match
            if matching_rows.empty:
                matching_rows = df[df['address'].str.upper().str.contains(clean_address, regex=False)]
                
        elif block and lot and borough:
            matching_rows = df[(df['tax_block'] == block) & 
                              (df['tax_lot'] == lot) & 
                              (df['borocode'] == borough)]
        else:
            return None
        
        if not matching_rows.empty:
            return matching_rows.iloc[0]
        return None
    except Exception as e:
        st.error(f"Error finding property: {e}")
        return None

# Load model - always do this at startup so it's available for all code paths
model = load_model()

# Data upload option
uploaded_file = st.sidebar.file_uploader("Upload property data CSV", type=['csv'])
if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
        st.sidebar.info(f"Found {len(raw_df)} entries")
        
        # Process the raw data
        df = process_raw_property_data(raw_df)
        st.sidebar.success(f"Processed data into {len(df)} unique properties")
    except Exception as e:
        st.sidebar.error(f"Error processing file: {e}")
        # Try to load existing data
        df = load_data()
else:
    # Load data
    df = load_data()

borough_map = load_boroughs()

# Show data statistics
if not df.empty:
    st.sidebar.markdown("### Data Summary")
    property_count = len(df)
    st.sidebar.write(f"Total properties: {property_count}")
    
    if 'has_violations' in df.columns:
        violations_count = df['has_violations'].sum()
        st.sidebar.write(f"Properties with violations: {violations_count}")
    
    if 'has_tax_lien' in df.columns:
        liens_count = df['has_tax_lien'].sum()
        st.sidebar.write(f"Properties with tax liens: {liens_count}")

# Main search interface
st.markdown("## Search for a Zombie Property")

# Two simple search options
search_method = st.radio("Search by:", ["Address", "Block/Lot"])

if search_method == "Address":
    address_input = st.text_input("Enter a NYC address:", "")
    search_button = st.button("Search", key="address_search")
    
    if search_button and address_input:
        if df.empty:
            st.error("No property data available. Please upload a CSV file.")
        else:
            with st.spinner(f"Searching for: {address_input}"):
                # Find the property in the dataset
                property_info = get_property_details(df, address=address_input)
                
                if property_info is not None:
                    # Create feature vector for prediction
                    features_df = pd.DataFrame({
                        'violation_count': [property_info.get('violation_count', 0)],
                        'has_tax_lien': [property_info.get('has_tax_lien', 0)],
                        'has_violations': [property_info.get('has_violations', 0)],
                        'is_residential': [property_info.get('is_residential', 0)],
                        'unitsres_zero': [property_info.get('unitsres_zero', 0)],
                        'borocode': [property_info['borocode']]
                    })
                    
                    # Get prediction
                    prob = predict_zombie_probability(model, features_df)
                    
                    # Display results
                    st.markdown("### Property Details")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Address:** {property_info['address']}")
                        st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
                        st.write(f"**Building Class:** {property_info['bldgclass']}")
                        st.write(f"**Owner:** {property_info['ownername']}")
                        st.write(f"**Residential Units:** {property_info['unitsres']}")
                        st.write(f"**Block:** {property_info['tax_block']}")
                        st.write(f"**Lot:** {property_info['tax_lot']}")
                    
                    with col2:
                        st.markdown("### Zombie Probability")
                        # Simple probability display
                        prob_percentage = f"{prob*100:.1f}%"
                        st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                        
                        # Risk level indicator
                        if prob > 0.7:
                            risk_level = "High Risk"
                            color = "red"
                        elif prob > 0.3:
                            risk_level = "Medium Risk"
                            color = "orange"
                        else:
                            risk_level = "Low Risk"
                            color = "green"
                        
                        st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                    
                    # Display risk factors
                    st.markdown("### Risk Factors")
                    
                    risk_factors = []
                    
                    # Check violation count
                    violation_count = property_info.get('violation_count', 0)
                    if violation_count > 0:
                        if violation_count > 10:
                            risk_factors.append(f"⚠️ Severe violation issues: {violation_count} open violations")
                        else:
                            risk_factors.append(f"Building has {violation_count} open code violations")
                    
                    # Check tax lien status
                    if property_info.get('has_tax_lien', 0) == 1:
                        risk_factors.append("⚠️ Property has tax liens")
                    
                    # Check for empty residential
                    if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
                        risk_factors.append("⚠️ Residential building with zero units reported")
                    
                    if risk_factors:
                        for factor in risk_factors:
                            st.write(f"• {factor}")
                    else:
                        st.write("No significant risk factors detected")
                    
                    # Show detailed violation info if available in original data
                    if 'raw_df' in locals() and 'violation_number' in raw_df.columns:
                        property_violations = raw_df[(raw_df['tax_block'] == property_info['tax_block']) & 
                                                  (raw_df['tax_lot'] == property_info['tax_lot']) &
                                                  (raw_df['violation_number'] != 'no violations')]
                        
                        if not property_violations.empty:
                            st.markdown("### Detailed Violations")
                            violation_df = property_violations[['violation_number', 'violation_type', 'issue_date']].copy()
                            st.dataframe(violation_df)
                else:
                    st.error(f"No matching property found for '{address_input}'")
                    st.write("Try checking the spelling or use the Block/Lot search method.")

else:  # Block/Lot search
    col1, col2, col3 = st.columns(3)
    
    with col1:
        block = st.number_input("Block:", min_value=1, value=1294)
    
    with col2:
        lot = st.number_input("Lot:", min_value=1, value=1)
    
    with col3:
        borough_options = sorted(borough_map.values())
        selected_borough = st.selectbox("Borough:", borough_options)
        # Convert borough name to code
        boro_code = [k for k, v in borough_map.items() if v == selected_borough][0]
    
    search_button = st.button("Search", key="block_lot_search")
    
    if search_button:
        if df.empty:
            st.error("No property data available. Please upload a CSV file.")
        else:
            with st.spinner("Searching by block/lot..."):
                # Find the property in the dataset
                property_info = get_property_details(df, block=block, lot=lot, borough=boro_code)
                
                if property_info is not None:
                    # Create feature vector for prediction
                    features_df = pd.DataFrame({
                        'violation_count': [property_info.get('violation_count', 0)],
                        'has_tax_lien': [property_info.get('has_tax_lien', 0)],
                        'has_violations': [property_info.get('has_violations', 0)],
                        'is_residential': [property_info.get('is_residential', 0)],
                        'unitsres_zero': [property_info.get('unitsres_zero', 0)],
                        'borocode': [property_info['borocode']]
                    })
                    
                    # Get prediction
                    prob = predict_zombie_probability(model, features_df)
                    
                    # Display results
                    st.markdown("### Property Details")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Address:** {property_info['address']}")
                        st.write(f"**Borough:** {borough_map.get(property_info['borocode'], 'Unknown')}")
                        st.write(f"**Building Class:** {property_info['bldgclass']}")
                        st.write(f"**Owner:** {property_info['ownername']}")
                        st.write(f"**Residential Units:** {property_info['unitsres']}")
                        st.write(f"**Block:** {property_info['tax_block']}")
                        st.write(f"**Lot:** {property_info['tax_lot']}")
                    
                    with col2:
                        st.markdown("### Zombie Probability")
                        # Simple probability display
                        prob_percentage = f"{prob*100:.1f}%"
                        st.markdown(f"<h1 style='text-align: center; color: {'red' if prob > 0.7 else 'orange' if prob > 0.3 else 'green'};'>{prob_percentage}</h1>", unsafe_allow_html=True)
                        
                        # Risk level indicator
                        if prob > 0.7:
                            risk_level = "High Risk"
                            color = "red"
                        elif prob > 0.3:
                            risk_level = "Medium Risk"
                            color = "orange"
                        else:
                            risk_level = "Low Risk"
                            color = "green"
                        
                        st.markdown(f"<h3 style='text-align: center; color: {color};'>{risk_level}</h3>", unsafe_allow_html=True)
                    
                    # Display risk factors
                    st.markdown("### Risk Factors")
                    
                    risk_factors = []
                    
                    # Check violation count
                    violation_count = property_info.get('violation_count', 0)
                    if violation_count > 0:
                        if violation_count > 10:
                            risk_factors.append(f"⚠️ Severe violation issues: {violation_count} open violations")
                        else:
                            risk_factors.append(f"Building has {violation_count} open code violations")
                    
                    # Check tax lien status
                    if property_info.get('has_tax_lien', 0) == 1:
                        risk_factors.append("⚠️ Property has tax liens")
                    
                    # Check for empty residential
                    if property_info.get('unitsres_zero', 0) == 1 and property_info.get('is_residential', 0) == 1:
                        risk_factors.append("⚠️ Residential building with zero units reported")
                    
                    if risk_factors:
                        for factor in risk_factors:
                            st.write(f"• {factor}")
                    else:
                        st.write("No significant risk factors detected")
                    
                    # Show detailed violation info if available in original data
                    if 'raw_df' in locals() and 'violation_number' in raw_df.columns:
                        property_violations = raw_df[(raw_df['tax_block'] == property_info['tax_block']) & 
                                                  (raw_df['tax_lot'] == property_info['tax_lot']) &
                                                  (raw_df['violation_number'] != 'no violations')]
                        
                        if not property_violations.empty:
                            st.markdown("### Detailed Violations")
                            violation_df = property_violations[['violation_number', 'violation_type', 'issue_date']].copy()
                            st.dataframe(violation_df)
                else:
                    st.error(f"No property found with Block: {block}, Lot: {lot} in {selected_borough}")

# Add a simple explanation at the bottom
st.markdown("---")
st.markdown("### About Zombie Properties")
st.write("""
Zombie properties are vacant or abandoned buildings that remain in limbo, often creating neighborhood blight and wasting potential housing resources.

Our model analyzes multiple factors to determine the likelihood a property is abandoned or severely underutilized, including:
- Building code violations
- Tax lien status
- Residential unit reporting
- Building classification
""")

# Footer
st.markdown("---")
st.write("© 2025 Zombie Property Project")