# PTV Visum Parallel Assignments
Example code to demonstrate how private transport assignments for multiple time periods can be run in parallel with PTV Visum.
Please contact [David Aspital](mailto:david.aspital@ptvgroup.com?subject=[GitHub]%20Parallel%20Assignments%20Tool), or log an issue if you have any quereies about this tool.
## Assumptions

The following assumptions and limitations are built in to the current version of the tool, although these can likely be overcome with small changes to the scripts:
* The tool is built for Visum 2021. Users of this tool are assumed to be familiar with PTV Visum and Transport Modelling terminology. For more info about PTV Visum, please visit: https://www.ptvgroup.com/en/solutions/products/ptv-visum/.
* 3 time periods AM, IP and PM are modelled in this example.
* Skims are the only data that are required to be brought back into the master file
* A fixed number of iteratons (3) is carried out between demand and supply

## Input File Creation
This section covers the template files and model definitions that need to be created in order for the tool to produce the correct sub-ordinate assignment files.

### Demand Files
 4 `.dmd` files are required for the tool to run:
* `DmdNoMats.dmd` – This is a template file to copy out the required demand data from the model (all demand data apart from the matrices). This file should not require any editing by the user.
*	`AM.dmd` – This is a demand data file that adds the matrices required for an AM assignment (demand and skim matrices) into the sub-ordinate version file.
*	`IP.dmd` – As above for an IP assignment
*	`PM.dmd` – As above for a PM assignment

The `AM.dmd`, `IP.dmd` and `PM.dmd` files can be created as follows:
1. Open the master version file
2. Navigate to *File > Save file as > Demand data...*
3. Give the file an arbitrary name
4. From the attribute selection dialog, uncheck all tables apart from *Matrices*
5. Save the file
6. Open the file in a text editor and delete from the matrices table all rows that do not correspond to the AM demand and skim matrices, and save as *AM.dmd*
7. Repeat Step 6. for the IP and PM time periods

### Procedure Files
3 `.xml` files are required for the tool to run:
* `AM.xml` – This is a section of the procedure sequence to run the AM assignment, with an additional step to save the skim matrices out at the end, and any Init assignment steps removed so that the assignment can be warm-started
*	`IP.xml` – As above for an IP assignment
*	`PM.xml` – As above for a PM assignment

The `AM.xml`, `IP.xml` and `PM.xml` files can be created as follows:
1. Open the master version file
2. Delete the procedure sequence apart from the section that runs the AM assignment and calculates skims
3. Add a 'Run script' procedure at the end and insert the following code into the dialog box:

```
import os
import pickle

folderpath = os.path.dirname(Visum.IO.CurrentVersionFile)
with open(f'{folderpath}\\skim_dict.pkl', 'rb') as f:
        skims = pickle.load(f)

mats = skims['AM']

for mat in mats:
	mtx = Visum.Net.Matrices.ItemByKey(mat)
	mtx.Save(folderpath+r"\\"+mats[mat],0)
```
4. Repeat steps 2 and 3 for the IP and PM time periods (noting that the `mats = skims['AM']` line in the script will need to be edited)

### Matrix Definitions
Two sets of lookups are required to ensure that the demand and skim matrices are exchanged correctly between the master and sub-ordinate files. These are produced by running the `process_matrix_att.py` script as follows:
1. Open the master version file
2. Open a matrix list via *Lists > OD demand > Matrices*, with no changes to the attribute selection
3. Save as a tabulator-separated attribute file (without extended attribute information) called `MatrixList.att`
4. Run the `process_matrix_att.py` script, making any adjustments necessary to accommodate your model setup (such as matrix naming conventions, demand segment codes etc)
5. This will produce the `skim_dict.pkl` and `demand_dict.pkl` files

## Ver File Setup
Extensive edits to the procedure sequence of the version file should not be required to run this tool. The edits required are as follows:
1. Uncheck or delete the sections of procedure sequence that correspond to the AM, IP and PM assignments (those exported earlier as .xml files)
2. Add a 'Run script' procedure and link to the `parallel_assignments.py` file
3. Edit the `parallel_assignments.py` file (line 76) with the procedure number of the *Go to procedure* procedure that controls iteration between demand and supply models


## Running Models
This setup should not introduce a large number of dependencies, however there are a few requirements:
1. The following files should be included in the same folder as the master version file:
    * AM.dmd
    * AM.xml
    * demand_dict.pkl
    * DmdNoMats.dmd
    * IP.dmd
    * IP.xml
    * parallel_assignments.py
    * PPM.dmd
    * PM.xml
    * skim_dict.pkl
2. The `parallel_assignments.py` file must be run as an external script from Visum; the code cannot be copied directly into the dialog box

## How the Script Works
The script works as follows:
* The required Python modules are imported. These are all installed by default into the PTV Visum environment and hence no additional setup is required.
* The skims and demand matrix definitions are loaded.
* A `Temp` sub-folder is created (if it does not exist already). This becomes the working directory for the tool and is where the matrices, Visum versions and supplementary files are stored. If you wish to amend this location, change line 72 in the script.
* The assignment demand matrices for each time period are saved out from the master version into the Temp folder.
* If it is the first pass of the model, the procedure files `AM.xml`, `IP.xml` and `PM.xml` are copied to the temp folder. The network is then exported to the `Net.net` file in the `Temp` folder, along with the demand data (apart from matrices). The *create_model* function is then run simultaneously for each time period, which opens Visum and imports the following data:
	* The network from `Net.net`
	* The demand data from `Dmd.dmd`
	* The relevant matrix definitions from `AM.dmd`, `IP.dmd`, or `PM.dmd`
	* The relevant matrices saved out from the master file
	* The relevant procedure sequence from `AM.xml`, `IP.xml`, or `PM.xml`
* The assignments are then run and the version files are saved. The skim matrices are then saved out of each of the files
* If it is not the first or final pass, the *run_model* function is run and the relevant Visum version files are opened, the assignment matrices are imported and the procedure sequence is re-run, using the current solution as the initial result. The version file is saved, and the skim matrices are saved out.
*	If it is the final pass of the model (defined as the *final_test* Boolean variable), the *run_final_model* function is run, which is similar to the *run_model* function, but can be expanded to take account of any variation in model running procedure that may be required (additional data to be exported, different convergence criteria etc).


## Extensions
Possible extensions that could be made to this script include:
* Exporting additional data (such as link flows) back from the sub-ordinate files into the master
* Additional time periods and demand segments
* Changes to the control for the final demand/supply iteration (Line 114)





