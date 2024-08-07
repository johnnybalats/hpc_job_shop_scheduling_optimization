import collections
from ortools.sat.python import cp_model

def calculate_horizon(df, max_decimal_length):
    '''
    Calculate the horizon
    '''
    horizon = 0

    for index, row in df.iterrows():

        horizon += (row['STANDARD_QTY_ACT1'] * 10 ** max_decimal_length) + (row['STANDARD_QTY_ACT2'] * 10 ** max_decimal_length) + (row['STANDARD_QTY_ACT3'] * 10 ** max_decimal_length)

    return int(horizon)