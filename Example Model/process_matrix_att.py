import pandas as pd
import pickle

time_periods = ['AM', 'IP', 'PM']
aucs = ['CB', 'CC', 'CO', 'HGV', 'LGV']

# Name of attribute that is used as the identifier for matrices
id_col = 'NAME'

demand_prefix = 'Demand '
dist_skim_prefix = 'Trip distance '
time_skim_prefix = 'tCur '
toll_skim_prefix = 'Toll '
skim_prefixes = [dist_skim_prefix, time_skim_prefix, toll_skim_prefix]

matrices = pd.read_csv('MatrixList.att', sep="\t", header=2, skiprows=10)

# Demand matrices (assumes DSegs are named as *AUC*_*TOD*)
demand_dict = {}
for t in time_periods:
    time_dict = {}
    for a in aucs:
        mat_num = matrices.loc[matrices[id_col]==f'{demand_prefix}{a}_{t}']['$MATRIX:NO'].squeeze()
        mat_file = matrices.loc[matrices[id_col]==f'{demand_prefix}{a}_{t}'][id_col].squeeze()+'.mtx'
        time_dict[mat_num] = mat_file
    demand_dict[t] = time_dict


# Skim matrices (assumes DSegs are named as *AUC*_*TOD*)
skim_dict = {}
for t in time_periods:
    time_dict = {}
    for a in aucs:
        for p in skim_prefixes:
            mat_num = matrices.loc[matrices[id_col]==f'{p}{a}_{t}']['$MATRIX:NO'].squeeze()
            mat_file = matrices.loc[matrices[id_col]==f'{p}{a}_{t}'][id_col].squeeze()+'.mtx'
            time_dict[mat_num] = mat_file
    skim_dict[t] = time_dict

with open('demand_dict.pkl', 'wb') as f:
    pickle.dump(demand_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

with open('skim_dict.pkl', 'wb') as f:
    pickle.dump(skim_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
