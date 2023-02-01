import pandas as pd
import streamlit as st
import numpy as np
from scipy import interpolate
import altair as alt

def get_user_inputs():
  col1, col2, col3, col4 = st.columns(4)
  
  # get input from user for temperature and altitude and weight
  with col1:
    user_temp = st.number_input('Enter Temp (F)', value=60, step=1)
  with col2:
    user_alt = st.number_input('Enter Field Elevation (ft)', value=0, step=100)
  with col3:
    user_ac_weight = st.number_input('Enter Aircraft Weight (lbs)', value=56000, step=1000)
  with col4:
    user_runway_length = st.number_input('Enter Runway Length (ft)', value=8000, step=100)
  
  return user_temp, user_alt, user_ac_weight, user_runway_length

def calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp):
   # create the interpolation function based on the combined weighted curve
  dr = interpolate.interp1d(dr_temp_x_input_tendegrees, interp_y, kind='quadratic', fill_value='extrapolate')

  # create the altair chart of this curve for every degree on the x axis and run though function for plotted values
  source = pd.DataFrame({
    'Temp(F)': dr_temp_x_input_onedegrees,
    'Density Ratio': dr(dr_temp_x_input_onedegrees)
  })

  c = alt.Chart(source).mark_line().encode(
      x='Temp(F)',
      y='Density Ratio'
  )

 # st.altair_chart(c, use_container_width = True)

  # create the array of interpolated values based on the curve at every degree
  interp_dr_array = dr(dr_temp_x_input_onedegrees)
  # output the metric of the density ratio based on the inputs from the user and the interpolation function
  density_ratio_calculated = np.round(dr(user_temp),2)
  st.metric('Density Ratio', density_ratio_calculated, delta=None, delta_color="normal")
  
  return density_ratio_calculated
    
def calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length):
  # create the interpolation function based on the combined weighted curve
  min_go_interpolated_lower = interpolate.interp1d(runway_lengths_array, interp_ys_lower_weightcurve, kind='quadratic', fill_value='extrapolate')
  min_go_interpolated_upper = interpolate.interp1d(runway_lengths_array, interp_ys_upper_weightcurve, kind='quadratic', fill_value='extrapolate')

  mg_interp_array_lower = min_go_interpolated_lower(rwl_expanded)
  mg_interp_array_upper = min_go_interpolated_upper(rwl_expanded)
  min_go_calculated_lower = min_go_interpolated_lower(user_runway_length)
  min_go_calculated_upper = min_go_interpolated_upper(user_runway_length)
  
  final_min_go = (1-ratio_2)*min_go_calculated_lower + ratio_2*min_go_calculated_upper
  
  st.metric('MinGo', np.round(final_min_go,2), delta=None, delta_color="normal")

  # create the altair chart of this curve for every degree on the x axis and run though function for plotted values
  source = pd.DataFrame({
    'RWL': rwl_expanded,
    'MinGo': min_go_interpolated_lower(rwl_expanded)
  })

  c = alt.Chart(source).mark_line().encode(
      x='RWL',
      y='MinGo'
  )

 # st.altair_chart(c, use_container_width = True)

  # create the altair chart of this curve for every degree on the x axis and run though function for plotted values
  source = pd.DataFrame({
    'RWL': rwl_expanded,
    'MinGo': min_go_interpolated_upper(rwl_expanded)
  })

  c = alt.Chart(source).mark_line().encode(
      x='RWL',
      y='MinGo'
  )

#  st.altair_chart(c, use_container_width = True)
      
  return final_min_go

 
def main():
  
  # set streamlit config parameters
  st.set_page_config(page_title='Growler TOLD', page_icon='🗒️', layout="centered", initial_sidebar_state="auto", menu_items=None)
  
  # Set page attributes
  st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)
  
  st.title('Growler TOLD')
  st.caption('Disclaimer:   Always reference the PCL charts for official TOLD data.')
  st.write('')
  input_tab, max_dry_tab = st.tabs(['Inputs', 'MAX/Dry Runway'])
  
  # create numpy arrays for the x and y axis values for density ratio chart
  dr_temp_x_input_tendegrees = np.arange(-60,150, 10)
  dr_temp_x_input_onedegrees = np.arange(-60,141)
  dr_dr_y_input = np.arange(0.5,1.31, 0.01, dtype=float)
  
  # create lists and convert to numpy array of function values from every 10 degrees for each altitude curve on densiry ratio chart
  #dr_sealevel = [1.3,1.27,1.23,1.2,1.175,1.15,1.125,1.1,1.08,1.06,1.04,1.02,1.0,0.98,0.96,0.94,0.925,0.91,0.89,0.88,0.86]
  #dr_2k = [1.2,1.175,1.15,1.125,1.09,1.07,1.05,1.03,1.01,0.99,0.975,0.95,0.94,0.92,0.9,0.88,0.87,0.85,0.83, 0.82,0.81]
  #dr_4k = [1.12,1.09,1.06,1.04,1.02,0.99,0.975,0.96,0.94,0.925,0.9,0.88,0.87,0.85,0.83,0.82,0.8,0.78,0.775,0.765,0.76]
  #dr_6k = [1.04,1.02,0.99,0.97,0.94,0.925,0.91,0.88,0.87,0.85,0.84,0.825,0.8,0.78,0.775,0.76,0.74,0.73,0.72,0.71,0.7]
  #dr_8k = [0.96,0.94,0.92,0.9,0.875,0.86,0.83,0.82,0.81,0.79,0.78,0.76,0.74,0.73,0.715,0.7,0.69,0.68,0.675,0.67,0.66]
  dr_df = pd.read_csv('DensityRatio.csv')
  dr_sealevel = dr_df['dr_sealevel']
  dr_2k = dr_df['dr_2k']
  dr_4k = dr_df['dr_4k']
  dr_6k = dr_df['dr_6k']
  dr_8k = dr_df['dr_8k']
  
  dr_sealevel_array = np.array(dr_sealevel)
  dr_2k_array = np.array(dr_2k)
  dr_4k_array = np.array(dr_4k)
  dr_6k_array = np.array(dr_6k)
  dr_8k_array = np.array(dr_8k)
  
  mingo_df = pd.read_csv('MinGo.csv')
  mingo_dr_steps = mingo_df['DR']
  mingo_34 = mingo_df['34k-4k', '34k-5k', '34k-6k', '34k-7k', '34k-8k', '34k-9k', '34k-10k', '34k-11k', '34k-12k']
  mingo_38 = mingo_df['38k-4k', '38k-5k', '38k-6k', '38k-7k', '38k-8k', '38k-9k', '38k-10k', '38k-11k', '38k-12k']
  mingo_42 = mingo_df['42k-4k', '42k-5k', '42k-6k', '42k-7k', '42k-8k', '42k-9k', '42k-10k', '42k-11k', '42k-12k']
  mingo_46 = mingo_df['46k-4k', '46k-5k', '46k-6k', '46k-7k', '46k-8k', '46k-9k', '46k-10k', '46k-11k', '46k-12k']
  mingo_50 = mingo_df['50k-4k', '50k-5k', '50k-6k', '50k-7k', '50k-8k', '50k-9k', '50k-10k', '50k-11k', '50k-12k']
  mingo_54 = mingo_df['54k-4k', '54k-5k', '54k-6k', '54k-7k', '54k-8k', '54k-9k', '54k-10k', '54k-11k', '54k-12k']
  mingo_58 = mingo_df['58k-4k', '58k-5k', '58k-6k', '58k-7k', '58k-8k', '58k-9k', '58k-10k', '58k-11k', '58k-12k']
  mingo_62 = mingo_df['62k-4k', '62k-5k', '62k-6k', '62k-7k', '62k-8k', '62k-9k', '62k-10k', '62k-11k', '62k-12k']
  mingo_66 = mingo_df['66k-4k', '66k-5k', '66k-6k', '66k-7k', '66k-8k', '66k-9k', '66k-10k', '66k-11k', '66k-12k']
  
  
  min_go_34 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,0,0,0,0,0,0,60],
               '5k': [0,0,0,0,0,0,0,0,0],
               '6k': [0,0,0,0,0,0,0,0,0],
               '7k': [0,0,0,0,0,0,0,0,0],
               '8k': [0,0,0,0,0,0,0,0,0],
               '9k': [0,0,0,0,0,0,0,0,0],
               '10k': [0,0,0,0,0,0,0,0,0],
               '11k': [0,0,0,0,0,0,0,0,0],
               '12k': [0,0,0,0,0,0,0,0,0]}
  min_go_38 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,0,0,0,0,40,70,90],
               '5k': [0,0,0,0,0,0,0,0,60],
               '6k': [0,0,0,0,0,0,0,0,0],
               '7k': [0,0,0,0,0,0,0,0,0],
               '8k': [0,0,0,0,0,0,0,0,0],
               '9k': [0,0,0,0,0,0,0,0,0],
               '10k': [0,0,0,0,0,0,0,0,0],
               '11k': [0,0,0,0,0,0,0,0,0],
               '12k': [0,0,0,0,0,0,0,0,0]}
  min_go_42 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,0,0,0,75,80,105,115],
               '5k': [0,0,0,0,0,0,50,75,95],
               '6k': [0,0,0,0,0,0,0,50,70],
               '7k': [0,0,0,0,0,0,0,0,50],
               '8k': [0,0,0,0,0,0,0,0,0],
               '9k': [0,0,0,0,0,0,0,0,0],
               '10k': [0,0,0,0,0,0,0,0,0],
               '11k': [0,0,0,0,0,0,0,0,0],
               '12k': [0,0,0,0,0,0,0,0,0]}
  min_go_46 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,0,0,50,100,110,125,135],
               '5k': [0,0,0,0,0,50,90,105,120],
               '6k': [0,0,0,0,0,0,50,90,105],
               '7k': [0,0,0,0,0,0,0,50,90],
               '8k': [0,0,0,0,0,0,0,0,50],
               '9k': [0,0,0,0,0,0,0,0,0],
               '10k': [0,0,0,0,0,0,0,0,0],
               '11k': [0,0,0,0,0,0,0,0,0],
               '12k': [0,0,0,0,0,0,0,0,0]}
  min_go_50 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,0,30,90,120,130,135,-1],
               '5k': [0,0,0,0,30,90,115,125,135],
               '6k': [0,0,0,0,0,20,90,115,125],
               '7k': [0,0,0,0,0,0,60,90,115],
               '8k': [0,0,0,0,0,0,0,70,90],
               '9k': [0,0,0,0,0,0,0,0,80],
               '10k': [0,0,0,0,0,0,0,0,70],
               '11k': [0,0,0,0,0,0,0,0,0],
               '12k': [0,0,0,0,0,0,0,0,0]}
  min_go_54 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,0,60,100,110,140,145,-1,-1],
               '5k': [0,0,0,30,85,110,130,140,-1],
               '6k': [0,0,0,0,40,80,110,130,140],
               '7k': [0,0,0,0,0,35,100,110,130],
               '8k': [0,0,0,0,0,0,60,105,110],
               '9k': [0,0,0,0,0,0,0,80,110],
               '10k': [0,0,0,0,0,0,0,50,100],
               '11k': [0,0,0,0,0,0,0,0,60],
               '12k': [0,0,0,0,0,0,0,0,55]}
  min_go_58 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,80,100,120,130,150,-1,-1,-1],
               '5k': [0,0,30,90,110,130,145,150,-1],
               '6k': [0,0,0,35,90,110,130,145,150],
               '7k': [0,0,0,0,35,90,120,130,145],
               '8k': [0,0,0,0,0,80,100,125,130],
               '9k': [0,0,0,0,0,0,80,110,125],
               '10k': [0,0,0,0,0,0,50,100,120],
               '11k': [0,0,0,0,0,0,0,90,100],
               '12k': [0,0,0,0,0,0,0,80,95]}
  min_go_62 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [0,110,120,135,145,-1,-1,-1,-1],
               '5k': [0,0,90,115,130,145,155,-1,-1],
               '6k': [0,0,0,80,115,130,145,155,-1],
               '7k': [0,0,0,0,90,115,135,145,155],
               '8k': [0,0,0,0,50,110,120,140,145],
               '9k': [0,0,0,0,0,80,110,125,140],
               '10k': [0,0,0,0,0,50,95,120,135],
               '11k': [0,0,0,0,0,0,80,110,120],
               '12k': [0,0,0,0,0,0,50,110,120]}
  min_go_66 = {'DR': [1.1,1.05,1.0,0.95,0.9,0.85,0.8,0.75,0.7],
               '4k': [80,125,135,145,155,-1,-1,-1,-1],
               '5k': [30,80,115,130,145,155,-1,-1,-1],
               '6k': [0,0,80,110,130,145,155,-1,-1],
               '7k': [0,0,0,80,115,130,145,155,-1],
               '8k': [0,0,0,50,100,125,135,150,155],
               '9k': [0,0,0,0,80,110,125,140,150],
               '10k': [0,0,0,0,50,95,115,135,150],
               '11k': [0,0,0,0,0,80,110,125,135],
               '12k': [0,0,0,0,0,30,100,125,135]}

  
  min_go_34_df = pd.DataFrame(min_go_34)
  min_go_38_df = pd.DataFrame(min_go_38)
  min_go_42_df = pd.DataFrame(min_go_42)
  min_go_46_df = pd.DataFrame(min_go_46)
  min_go_50_df = pd.DataFrame(min_go_50)
  min_go_54_df = pd.DataFrame(min_go_54)
  min_go_58_df = pd.DataFrame(min_go_58)
  min_go_62_df = pd.DataFrame(min_go_62)
  min_go_66_df = pd.DataFrame(min_go_66)
  
  runway_lengths = [4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000]
  runway_lengths_array = np.array(runway_lengths)
  rwl_expanded = np.arange(4000, 12000, 100)
  
  with input_tab:
      with st.container():
        user_temp, user_alt, user_ac_weight, user_runway_length = get_user_inputs()
  
  # if the field elevation altitude is 0
  if user_alt == 0:
    interp_y = dr_sealevel_array
    with max_dry_tab:
        density_ratio_calculated = calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp)
    
  # if the field elevation altitude is between 0 and 2000 ft
  if 0 < user_alt <=2000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt)/2000
    interp_y = ((1-ratio)*dr_sealevel_array + (ratio)*dr_2k_array)
    with max_dry_tab:
        density_ratio_calculated = calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp)
    
  # if the field elevation altitude is between 2000 and 4000 ft
  if 2000 < user_alt <=4000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-2000)/2000
    interp_y = ((1-ratio)*dr_2k_array + (ratio)*dr_4k_array)
    with max_dry_tab:
        density_ratio_calculated = calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp)
    
  # if the field elevation altitude is between 4000 and 6000 ft
  if 4000 < user_alt <=6000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-4000)/2000
    interp_y = ((1-ratio)*dr_4k_array + (ratio)*dr_6k_array)
    with max_dry_tab:
        density_ratio_calculated = calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp)
    
  # if the field elevation altitude is between 6000 and 8000 ft
  if 6000 < user_alt <=8000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-6000)/2000
    interp_y = ((1-ratio)*dr_6k_array + (ratio)*dr_8k_array)
    with max_dry_tab:
        density_ratio_calculated = calc_density_ratio(interp_y, dr_temp_x_input_tendegrees, dr_temp_x_input_onedegrees, user_temp)
  
  if 34000 < user_ac_weight <= 38000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-34000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[8,1:] + (ratio_weight)*min_go_38_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[7,1:] + (ratio_weight)*min_go_38_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)
      
    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[7,1:] + (ratio_weight)*min_go_38_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[6,1:] + (ratio_weight)*min_go_38_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)
      
    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[6,1:] + (ratio_weight)*min_go_38_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[5,1:] + (ratio_weight)*min_go_38_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)
      
    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[5,1:] + (ratio_weight)*min_go_38_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[4,1:] + (ratio_weight)*min_go_38_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[4,1:] + (ratio_weight)*min_go_38_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[3,1:] + (ratio_weight)*min_go_38_df.iloc[3,1:])
      
      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[3,1:] + (ratio_weight)*min_go_38_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[2,1:] + (ratio_weight)*min_go_38_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[2,1:] + (ratio_weight)*min_go_38_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[1,1:] + (ratio_weight)*min_go_38_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[1,1:] + (ratio_weight)*min_go_38_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_34_df.iloc[0,1:] + (ratio_weight)*min_go_38_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

  if 38000 < user_ac_weight <= 42000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-38000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[8,1:] + (ratio_weight)*min_go_42_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[7,1:] + (ratio_weight)*min_go_42_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[7,1:] + (ratio_weight)*min_go_42_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[6,1:] + (ratio_weight)*min_go_42_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[6,1:] + (ratio_weight)*min_go_42_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[5,1:] + (ratio_weight)*min_go_42_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[5,1:] + (ratio_weight)*min_go_42_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[4,1:] + (ratio_weight)*min_go_42_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[4,1:] + (ratio_weight)*min_go_42_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[3,1:] + (ratio_weight)*min_go_42_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[3,1:] + (ratio_weight)*min_go_42_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[2,1:] + (ratio_weight)*min_go_42_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[2,1:] + (ratio_weight)*min_go_42_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[1,1:] + (ratio_weight)*min_go_42_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[1,1:] + (ratio_weight)*min_go_42_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_38_df.iloc[0,1:] + (ratio_weight)*min_go_42_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

  if 42000 < user_ac_weight <= 46000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-42000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[8,1:] + (ratio_weight)*min_go_46_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[7,1:] + (ratio_weight)*min_go_46_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[7,1:] + (ratio_weight)*min_go_46_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[6,1:] + (ratio_weight)*min_go_46_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[6,1:] + (ratio_weight)*min_go_46_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[5,1:] + (ratio_weight)*min_go_46_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[5,1:] + (ratio_weight)*min_go_46_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[4,1:] + (ratio_weight)*min_go_46_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[4,1:] + (ratio_weight)*min_go_46_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[3,1:] + (ratio_weight)*min_go_46_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[3,1:] + (ratio_weight)*min_go_46_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[2,1:] + (ratio_weight)*min_go_46_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[2,1:] + (ratio_weight)*min_go_46_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[1,1:] + (ratio_weight)*min_go_46_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[1,1:] + (ratio_weight)*min_go_46_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_42_df.iloc[0,1:] + (ratio_weight)*min_go_46_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)  

  if 46000 < user_ac_weight <= 50000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-46000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[8,1:] + (ratio_weight)*min_go_50_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[7,1:] + (ratio_weight)*min_go_50_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[7,1:] + (ratio_weight)*min_go_50_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[6,1:] + (ratio_weight)*min_go_50_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[6,1:] + (ratio_weight)*min_go_50_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[5,1:] + (ratio_weight)*min_go_50_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[5,1:] + (ratio_weight)*min_go_50_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[4,1:] + (ratio_weight)*min_go_50_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[4,1:] + (ratio_weight)*min_go_50_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[3,1:] + (ratio_weight)*min_go_50_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[3,1:] + (ratio_weight)*min_go_50_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[2,1:] + (ratio_weight)*min_go_50_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[2,1:] + (ratio_weight)*min_go_50_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[1,1:] + (ratio_weight)*min_go_50_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[1,1:] + (ratio_weight)*min_go_50_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_46_df.iloc[0,1:] + (ratio_weight)*min_go_50_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)
      
  if 50000 < user_ac_weight <= 54000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-50000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[8,1:] + (ratio_weight)*min_go_54_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[7,1:] + (ratio_weight)*min_go_54_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[7,1:] + (ratio_weight)*min_go_54_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[6,1:] + (ratio_weight)*min_go_54_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[6,1:] + (ratio_weight)*min_go_54_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[5,1:] + (ratio_weight)*min_go_54_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[5,1:] + (ratio_weight)*min_go_54_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[4,1:] + (ratio_weight)*min_go_54_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[4,1:] + (ratio_weight)*min_go_54_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[3,1:] + (ratio_weight)*min_go_54_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[3,1:] + (ratio_weight)*min_go_54_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[2,1:] + (ratio_weight)*min_go_54_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[2,1:] + (ratio_weight)*min_go_54_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[1,1:] + (ratio_weight)*min_go_54_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[1,1:] + (ratio_weight)*min_go_54_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_50_df.iloc[0,1:] + (ratio_weight)*min_go_54_df.iloc[0,1:])
      
      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

  if 54000 < user_ac_weight <= 58000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-54000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[8,1:] + (ratio_weight)*min_go_58_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[7,1:] + (ratio_weight)*min_go_58_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[7,1:] + (ratio_weight)*min_go_58_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[6,1:] + (ratio_weight)*min_go_58_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[6,1:] + (ratio_weight)*min_go_58_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[5,1:] + (ratio_weight)*min_go_58_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[5,1:] + (ratio_weight)*min_go_58_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[4,1:] + (ratio_weight)*min_go_58_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[4,1:] + (ratio_weight)*min_go_58_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[3,1:] + (ratio_weight)*min_go_58_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[3,1:] + (ratio_weight)*min_go_58_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[2,1:] + (ratio_weight)*min_go_58_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[2,1:] + (ratio_weight)*min_go_58_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[1,1:] + (ratio_weight)*min_go_58_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[1,1:] + (ratio_weight)*min_go_58_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_54_df.iloc[0,1:] + (ratio_weight)*min_go_58_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

  if 58000 < user_ac_weight <= 62000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-58000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[8,1:] + (ratio_weight)*min_go_62_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[7,1:] + (ratio_weight)*min_go_62_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[7,1:] + (ratio_weight)*min_go_62_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[6,1:] + (ratio_weight)*min_go_62_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[6,1:] + (ratio_weight)*min_go_62_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[5,1:] + (ratio_weight)*min_go_62_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[5,1:] + (ratio_weight)*min_go_62_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[4,1:] + (ratio_weight)*min_go_62_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[4,1:] + (ratio_weight)*min_go_62_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[3,1:] + (ratio_weight)*min_go_62_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[3,1:] + (ratio_weight)*min_go_62_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[2,1:] + (ratio_weight)*min_go_62_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[2,1:] + (ratio_weight)*min_go_62_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[1,1:] + (ratio_weight)*min_go_62_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[1,1:] + (ratio_weight)*min_go_62_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_58_df.iloc[0,1:] + (ratio_weight)*min_go_62_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)
      
  if 62000 < user_ac_weight <= 66000:
    # create a ratio for biasing weights on combining curves
    ratio_weight = (user_ac_weight-62000)/4000
    
    if 0.70 <= density_ratio_calculated <= 0.75:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[8,1:] + (ratio_weight)*min_go_66_df.iloc[8,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[7,1:] + (ratio_weight)*min_go_66_df.iloc[7,1:])

      ratio_2 = (density_ratio_calculated-0.7)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.75 < density_ratio_calculated <= 0.8:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[7,1:] + (ratio_weight)*min_go_66_df.iloc[7,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[6,1:] + (ratio_weight)*min_go_66_df.iloc[6,1:])

      ratio_2 = (density_ratio_calculated-0.75)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.8 < density_ratio_calculated <= 0.85:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[6,1:] + (ratio_weight)*min_go_66_df.iloc[6,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[5,1:] + (ratio_weight)*min_go_66_df.iloc[5,1:])

      ratio_2 = (density_ratio_calculated-0.8)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.85 < density_ratio_calculated <= 0.9:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[5,1:] + (ratio_weight)*min_go_66_df.iloc[5,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[4,1:] + (ratio_weight)*min_go_66_df.iloc[4,1:])

      ratio_2 = (density_ratio_calculated-0.85)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.9 < density_ratio_calculated <= 0.95:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[4,1:] + (ratio_weight)*min_go_66_df.iloc[4,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[3,1:] + (ratio_weight)*min_go_66_df.iloc[3,1:])

      ratio_2 = (density_ratio_calculated-0.9)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 0.95 < density_ratio_calculated <= 1.0:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[3,1:] + (ratio_weight)*min_go_66_df.iloc[3,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[2,1:] + (ratio_weight)*min_go_66_df.iloc[2,1:])

      ratio_2 = (density_ratio_calculated-0.95)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.0 < density_ratio_calculated <= 1.05:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[2,1:] + (ratio_weight)*min_go_66_df.iloc[2,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[1,1:] + (ratio_weight)*min_go_66_df.iloc[1,1:])

      ratio_2 = (density_ratio_calculated-1.0)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

    if 1.05 < density_ratio_calculated <= 1.1:
      interp_ys_lower_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[1,1:] + (ratio_weight)*min_go_66_df.iloc[1,1:])
      interp_ys_upper_weightcurve = ((1-ratio_weight)*min_go_62_df.iloc[0,1:] + (ratio_weight)*min_go_66_df.iloc[0,1:])

      ratio_2 = (density_ratio_calculated-1.05)/0.05
      with max_dry_tab:
          final_min_go = calc_min_go(ratio_2, runway_lengths_array, interp_ys_lower_weightcurve, interp_ys_upper_weightcurve, rwl_expanded, user_runway_length)

      
if __name__ == "__main__":
  main()
