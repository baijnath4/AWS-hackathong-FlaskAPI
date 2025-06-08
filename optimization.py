# optimization_plugin.py

import pandas as pd


def optimize_production() -> str:
    machine=pd.read_csv('machine_df.csv')
    employee=pd.read_csv('employee_df.csv')

    return machine, employee


    