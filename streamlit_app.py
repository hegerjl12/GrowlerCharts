import pandas as pd
import streamlit as st
import numpy as np
from scipy import interpolate
import altair as alt


def main():
  
  st.set_page_config(page_title='F18 Toolbox', page_icon='✈', layout="centered", initial_sidebar_state="auto", menu_items=None)
  
  dr_temp_x_input_tendegrees = np.arange(-60,150, 10)
  dr_temp_x_input_onedegrees = np.arange(-60,141)
  dr_dr_y_input = np.arange(0.5,1.31, 0.01, dtype=float)
  
  dr_sealevel = [1.3,1.27,1.23,1.2,1.175,1.15,1.125,1.1,1.08,1.06,1.04,1.02,1.0,0.98,0.96,0.94,0.925,0.91,0.89,0.88,0.86]
  dr_2k = [1.2,1.175,1.5,1.125,1.09,1.07,1.05,1.03,1.01,0.99,0.975,0.95,0.94,0.92,0.9,0.88,0.87,0.85,0.83, 0.82,0.81]
  dr_sealevel_array = np.array(dr_sealevel)
  dr_2k_array = np.array(dr_2k)
  
  user_temp = st.number_input('Enter Temp (F)')
  user_alt = st.number_input('Enter Field Altitude (FT)')
  
  if user_alt == 0:
    dr = interpolate.interp1d(dr_temp_x_input_tendegrees, dr_sealevel_array, kind='quadratic', fill_value='extrapolate')
    
    source = pd.DataFrame({
      'Temp(F)': dr_temp_x_input_onedegrees,
      'Density Ratio': dr(dr_temp_x_input_onedegrees)
    })

    c = alt.Chart(source).mark_line().encode(
        x='Temp(F)',
        y='Density Ratio'
    )

    st.altair_chart(c, use_container_width = True)

    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
    
  if 0 < user_alt <=2000:
    ratio = user_alt/2000
    interp_y = (ratio*dr_sealevel_array + (1-ratio)*dr_2k_array)
    
    dr = interpolate.interp1d(dr_temp_x_input_tendegrees, interp_y, kind='quadratic', fill_value='extrapolate')
    
    source = pd.DataFrame({
      'Temp(F)': dr_temp_x_input_onedegrees,
      'Density Ratio': dr(dr_temp_x_input_onedegrees)
    })

    c = alt.Chart(source).mark_line().encode(
        x='Temp(F)',
        y='Density Ratio'
    )

    st.altair_chart(c, use_container_width = True)

    interp_dr_array = dr(dr_temp_x_input_onedegrees)
    st.metric('Density Ratio', np.round(dr(user_temp), 2), delta=None, delta_color="normal")
  
if __name__ == "__main__":
  main()
