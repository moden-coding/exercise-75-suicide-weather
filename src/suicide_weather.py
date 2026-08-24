#!/usr/bin/env python3

import pandas as pd

def suicide_fractions():
    pass
    #Copy from previous exercise
    
def suicide_weather():
    pass

def main():
    suicide_rows, temperature_rows, common_rows, correlation = suicide_weather()
    print(f"Suicide DataFrame has {suicide_rows} rows")
    print(f"Temperature DataFrame has {temperature_rows} rows")
    print(f"Common DataFrame has {common_rows} rows")
    print(f"Spearman correlation: {correlation}")

if __name__ == "__main__":
    main()
