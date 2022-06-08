import pandas as pd
import streamlit as st
import numpy as np
from scipy import interpolate
import altair as alt


def main():
  
  # set streamlit config parameters
  st.set_page_config(page_title='F18 Toolbox', page_icon='✈', layout="centered", initial_sidebar_state="auto", menu_items=None)
  
  # create numpy arrays for the x and y axis values for density ratio chart
  dr_temp_x_input_tendegrees = np.arange(-60,150, 10)
  dr_temp_x_input_onedegrees = np.arange(-60,141)
  dr_dr_y_input = np.arange(0.5,1.31, 0.01, dtype=float)
  
  # create lists and convert to numpy array of function values from every 10 degrees for each altitude curve on densiry ratio chart
  dr_sealevel = [1.3,1.27,1.23,1.2,1.175,1.15,1.125,1.1,1.08,1.06,1.04,1.02,1.0,0.98,0.96,0.94,0.925,0.91,0.89,0.88,0.86]
  dr_2k = [1.2,1.175,1.15,1.125,1.09,1.07,1.05,1.03,1.01,0.99,0.975,0.95,0.94,0.92,0.9,0.88,0.87,0.85,0.83, 0.82,0.81]
  dr_4k = [1.12,1.09,1.06,1.04,1.02,0.99,0.975,0.96,0.94,0.925,0.9,0.88,0.87,0.85,0.83,0.82,0.8,0.78,0.775,0.765,0.76]
  dr_6k = [1.04,1.02,0.99,0.97,0.94,0.925,0.91,0.88,0.87,0.85,0.84,0.825,0.8,0.78,0.775,0.76,0.74,0.73,0.72,0.71,0.7]
  dr_8k = [0.96,0.94,0.92,0.9,0.875,0.86,0.83,0.82,0.81,0.79,0.78,0.76,0.74,0.73,0.715,0.7,0.69,0.68,0.675,0.67,0.66]
  dr_sealevel_array = np.array(dr_sealevel)
  dr_2k_array = np.array(dr_2k)
  dr_4k_array = np.array(dr_4k)
  dr_6k_array = np.array(dr_6k)
  dr_8k_array = np.array(dr_8k)
  
  # get input from user for temperature and altitude
  user_temp = st.number_input('Enter Temp (F)', value=60, step=1)
  user_alt = st.number_input('Enter Field Altitude (FT)', value=0, step=100)
  
  # if the field elevation altitude is 0
  if user_alt == 0:
    # create the interpolation function based on the sea level curve
    dr = interpolate.interp1d(dr_temp_x_input_tendegrees, dr_sealevel_array, kind='quadratic', fill_value='extrapolate')
    
    # create the altair chart of this curve for every degree on the x axis and run though function for plotted values
    source = pd.DataFrame({
      'Temp(F)': dr_temp_x_input_onedegrees,
      'Density Ratio': dr(dr_temp_x_input_onedegrees)
    })

    c = alt.Chart(source).mark_line().encode(
        x='Temp(F)',
        y='Density Ratio'
    )
    
    st.altair_chart(c, use_container_width = True)

    # create the array of interpolated values based on the curve at every degree
    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    # output the metric of the density ratio based on the inputs from the user and the interpolation function
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
  # if the field elevation altitude is between 0 and 2000 ft
  if 0 < user_alt <=2000:
    # create a ratio for biasing weights on combining curves
    ratio = user_alt/2000
    interp_y = ((1-ratio)*dr_sealevel_array + (ratio)*dr_2k_array)
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
    
    st.altair_chart(c, use_container_width = True)

    # create the array of interpolated values based on the curve at every degree
    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    # output the metric of the density ratio based on the inputs from the user and the interpolation function
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
    
  # if the field elevation altitude is between 2000 and 4000 ft
  if 2000 < user_alt <=4000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-2000)/2000
    interp_y = ((1-ratio)*dr_2k_array + (ratio)*dr_4k_array)
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

    st.altair_chart(c, use_container_width = True)
    
    # create the array of interpolated values based on the curve at every degree
    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    # output the metric of the density ratio based on the inputs from the user and the interpolation function
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
  
  # if the field elevation altitude is between 4000 and 6000 ft
  if 4000 < user_alt <=6000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-4000)/2000
    interp_y = ((1-ratio)*dr_4k_array + (ratio)*dr_6k_array)
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

    st.altair_chart(c, use_container_width = True)
    
    # create the array of interpolated values based on the curve at every degree
    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    # output the metric of the density ratio based on the inputs from the user and the interpolation function
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
    
  # if the field elevation altitude is between 6000 and 8000 ft
  if 6000 < user_alt <=8000:
    # create a ratio for biasing weights on combining curves
    ratio = (user_alt-6000)/2000
    interp_y = ((1-ratio)*dr_6k_array + (ratio)*dr_8k_array)
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

    st.altair_chart(c, use_container_width = True)

    # create the array of interpolated values based on the curve at every degree
    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    # output the metric of the density ratio based on the inputs from the user and the interpolation function
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
    
    
    
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
   # min_go_38
 #   min_go_42
 #   min_go_46
 #   min_go_50
 #   min_go_54
  #  min_go_58
  #  min_go_62
  #  min_go_66
    
    
    min_go_34_df = pd.DataFrame(min_go_34)
    st.write(min_go_34_df)
    
    
    
if __name__ == "__main__":
  main()
