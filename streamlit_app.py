import pandas as pd
import streamlit as st
import numpy as np



def main():
  
  dr_temp_x = np.arange(-60,141)
  dr_dr_y = np.arange(0.5,1.31, 0.01)
  
  st.write(dr_dr_y)
  
  
if __name__ == "__main__":
  main()
