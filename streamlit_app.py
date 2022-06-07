import pandas as pd
import streamlit as st
import numpy as np
from scipy import interpolate


def main():
  
  dr_temp_x = np.arange(-60,150, 10)
  dr_dr_y = np.arange(0.5,1.31, 0.01, dtype=float)
  dr_sealevel = [1.3,1.27,1.23,1.2,1.175,1.125,1.1,1.08,1.06,1.04,1.02,1.0,0.98,0.96,0.94,0.925,0.91,0.89,0.88,0.86]
  dr_sealevel_array = np.array(dr_sealevel)
  
  dr = interpolate.interp1d(dr_temp_x, dr_sealevel_array)
  
  st.write(dr(60))
  
  
if __name__ == "__main__":
  main()
