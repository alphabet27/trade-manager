import pandas as pd

def var_reader(df):    
    with open('sample_database/addnl_stock.csv', 'r') as f:
        for line in f:
            df = pd.concat( [df, pd.DataFrame([tuple(line.strip().split(','))])], ignore_index=True )



