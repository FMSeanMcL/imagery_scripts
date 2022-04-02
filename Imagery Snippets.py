# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 07:57:08 2022

@author: smclaugh1
"""

import arcpy
from arcpy import env
#env.workspace = r"F:\Orthoimagery_gdb\Safford_Imagery.gdb"
env.workspace = r"C:\Temp\safford\Safford_Imagery.gdb"
env.overwriteOutput = True

# hardcoded site for development
site = "Safford"

#mos_dataset = r"F:\Orthoimagery_gdb\Safford_Imagery.gdb\S_Safford_3vG_ComSat"
mos_dataset = r"C:\Temp\safford\Safford_Imagery.gdb" + "\\S_" + site + "_3vG_ComSat"

# Location for export mosaic dataset paths
bad_paths = r"C:\Temp\mosaic test\mosaic test.gdb\bad_paths"


# Deleting existing objects
if "mosaic_layer":
    arcpy.management.Delete("mosaic_layer")
if bad_paths:
    arcpy.management.Delete(bad_paths)
    
    
# Create layer in memory for processing
arcpy.management.MakeMosaicLayer(mos_dataset, "mosaic_layer")

# Select layer by attribute
arcpy.management.SelectLayerByAttribute("mosaic_layer\Footprint", "NEW_SELECTION", "'Site_Name' IS NULL", None)

print('calculating fields')
# Calculate fields
try:
    arcpy.management.CalculateField("mosaic_layer", "Site_Name", "'" + site + "'", "ARCADE", '', "TEXT", "NO_ENFORCE_DOMAINS")
except Exception as e:
    print(f"No selection to calculate{e}")

# Output location for ExportMosaicDatasetPaths
#out_fgdb = r"C:\Users\smclaugh1.FSL0\Documents\Pro Projects\Fix Mosaic Paths\Fix Mosaic Paths.gdb"
out_fgdb = r"C:\Temp\mosaic test\mosaic test.gdb"

arcpy.management.ExportMosaicDatasetPaths(mos_dataset, out_fgdb + "\\bad_paths", '#', "BROKEN","RASTER")


# Mosaic dataset paths to fix
paths_list = [["F:\imagery1\Orthoimagery_gdb","F:\Orthoimagery_gdb"],
              ["F:\imagery1\Orthoimagery","F:\Orthoimagery"],
              ["G:\Imagery2\Orthoimagery","G:\Orthoimagery"]
              ]
# Repair the mosaic paths using the paths_list above
arcpy.management.RepairMosaicDatasetPaths(mos_dataset, paths_list)


#clean up
if "mosaic_layer":
    arcpy.management.Delete("mosaic_layer")
    
    
    
# Generic "arcpy.management.Delete" statement    
''' 
try:
    arcpy.management.Delete("mosaic_layer")
except Exception as e:
    print(f"Exception! {e}")
'''   