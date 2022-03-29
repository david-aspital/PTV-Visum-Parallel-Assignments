import os
import win32com.client as com
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path
from shutil import copy
import pickle


def create_model(temp_path, time_period):
    # Function to open and run individual models 

    # Launch Visum instance
    Visum = com.Dispatch("Visum.Visum.220")       
    # Load network, demand, matrices and procedure sequence
    Visum.IO.LoadNet(f"{temp_path}\\Net.net", False, None, None, False, False, -1)
    Visum.IO.LoadDemandFile(f"{temp_path}\\Dmd.dmd", True)
    Visum.IO.LoadDemandFile(f"{temp_path}\\{time_period}.dmd", True)
    demand_tp = demand[time_period]
    for mat in demand_tp:
        mtx = Visum.Net.Matrices.ItemByKey(mat)
        mtx.Open(temp_path+f'\\{demand_tp[mat]}', 0)
    Visum.Procedures.OpenXmlWithOptions(f'{temp_path}\\{time_period}.xml', True, False, 0)
    # Save initial version
    Visum.SaveVersion(f"{temp_path}\\{time_period}.ver")
    # Run assignment
    Visum.Procedures.Execute()
    Visum.SaveVersion(f"{temp_path}\\{time_period}.ver")
    # Init Visum object to close file
    Visum = None

def run_model(temp_path, time_period):
    # Function to open and run individual models 

    # Launch Visum instance
    Visum = com.Dispatch("Visum.Visum.220")       
    # Load network, demand, matrices and procedure sequence
    Visum.LoadVersion(f"{temp_path}\\{time_period}.ver")
    demand_tp = demand[time_period]
    for mat in demand_tp:
        mtx = Visum.Net.Matrices.ItemByKey(mat)
        mtx.Open(temp_path+f'\\{demand_tp[mat]}', 0)
    # Run assignment
    Visum.Procedures.Execute()
    Visum.SaveVersion(f"{temp_path}\\{time_period}.ver")
    # Init Visum object to close file
    Visum = None

def run_final_model(temp_path, time_period):
    # Function to open and run individual models, including all steps  

    # Launch Visum instance
    Visum = com.Dispatch("Visum.Visum.220")       
    # Load network, demand, matrices and procedure sequence
    Visum.LoadVersion(f"{temp_path}\\{time_period}.ver")
    demand_tp = demand[time_period]
    for mat in demand_tp:
        mtx = Visum.Net.Matrices.ItemByKey(mat)
        mtx.Open(temp_path+f'\\{demand_tp[mat]}', 0)
    # Run assignment
    Visum.Procedures.Execute()

    # Space to add special considerations for final assignments (bringing data back into master file, different convergence criteria etc)
    # ...

    Visum.SaveVersion(f"{temp_path}\\{time_period}.ver")
    # Init Visum object to close file
    Visum = None

if __name__ == '__main__':

    # Create Temp directory to store files in
    temp_path = os.path.dirname(os.path.abspath(__file__))+r"\\Temp"
    Path(temp_path).mkdir(parents=True, exist_ok=True)

    # GoToProcedure procedure number
    GTP_num = 25

    # Filenames for individual assignment files
    time_periods = ['AM', 'IP', 'PM']

    # Generate list of filepaths for models
    models = [(temp_path, x) for x in time_periods]

    # Only required for first pass
    if Visum.Procedures.Operations.ItemByKey(GTP_num).JumpBackParameters.AttValue('CurrentCounter') == 0:
        # Copy required files to Temp folder
        for tp in time_periods:
            copy(f'{tp}.xml', f"{temp_path}\\{tp}.xml")
            copy(f'{tp}.dmd', f"{temp_path}\\{tp}.dmd")
        copy(f'skim_dict.pkl', f"{temp_path}\\skim_dict.pkl")
        copy(f'demand_dict.pkl', f"{temp_path}\\demand_dict.pkl")

        # Save relevant components of main file
        net_file = f"{temp_path}\\Net.net"
        dmd_file = f"{temp_path}\\Dmd.dmd"
        Visum.IO.SaveDemandFile(dmd_file, False, "DmdNoMats.dmd")
        Visum.IO.SaveNet(net_file, editableOnly=True)

    # Dictionaries for skims and demand matrices
    with open(f'{temp_path}\\skim_dict.pkl', 'rb') as f:
        skims = pickle.load(f)

    with open(f'{temp_path}\\demand_dict.pkl', 'rb') as f:
        demand = pickle.load(f)

    # Save matrices to temp folder
    for tp in time_periods:
        demand_tp = demand[tp]
        for mat in demand_tp:
            mtx = Visum.Net.Matrices.ItemByKey(mat)
            mtx.Save(temp_path+f'\\{demand_tp[mat]}', 0)

    # Define test for final assignment here (standard is if Loop attribute is 3)
    final_test = True if Visum.Procedures.Operations.ItemByKey(GTP_num).JumpBackParameters.AttValue('CurrentCounter') == 3 else False
     
    # Multi-thread assignments
    with Pool(5) as p:
        if Visum.Procedures.Operations.ItemByKey(GTP_num).JumpBackParameters.AttValue('CurrentCounter') == 0:
            p.starmap(create_model, models)
        elif final_test:
            p.starmap(run_final_model, models)
        else:
            p.starmap(run_model, models)

    # Bring matrices back into master file
    for tp in time_periods:
        skims_tp = skims[tp]
        for mat in skims_tp:
            mtx = Visum.Net.Matrices.ItemByKey(mat)
            mtx.Open(f'{temp_path}\\{skims_tp[mat]}', 0)

    # Bring attributes back into master file after final assignment
    if final_test:
        for time_period in time_periods:
            # Space to add special considerations for final assignments (bringing data back into master file etc)
            # ...
            break
