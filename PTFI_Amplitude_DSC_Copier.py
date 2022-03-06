'''
Sean McLaughlin (smclaugh1@fmi.com)
This script copies files from the source folders to our destination
folder and adds them to a mosaic.

3/4/2022 - Modified to look for ascending as well as descending 
           amplitude files.
'''


import arcpy
from arcpy import env
import glob
import os
from subprocess import call
import datetime

# Set up workspace
env.workspace = r"F:\imagery1\Orthoimagery_gdb\PTFI_Imagery.gdb\S_PTFI_Amplitude"
mos_dataset = env.workspace
sr = arcpy.SpatialReference(32753)    

# Set up directories
#src = r"\\geospatialnapsa01.file.core.windows.net\insar\GRS_LL\Amplitudes\DSC"
#src = r"\\geospatialnapsa01.file.core.windows.net\insar\GRS_LL\Amplitudes"
src = r"\\fmi.com\data\PHX\GMX_InSAR\InSAR_from_3vG\GRS_LL\Amplitudes"
dst = r"G:\Imagery2\Orthoimagery\PTFI\TerraSARX"
year = str(datetime.datetime.now().year)
srcfiles=[]
dstfiles=[]
file = ""

# Get files in src folder
for srcpath in glob.glob(src +  "/**/*8b.tif", recursive=True):
    file = os.path.basename(srcpath)
    if int(file[0:4]) > 2020:
        srcfiles.append(file)

# Get files in dest folder    
for dstpath in glob.glob(dst +  "/**/*8b.tif", recursive=True):
    file = os.path.basename(dstpath)
    dstfiles.append(file)

# Compare file lists    
files_to_process =[]
for file in srcfiles:
    if file not in dstfiles:
        files_to_process.append(file)
        #year = os.path.basename(file)[0:4]       
dstfolder = dst + "\\" + year + "\\" + year + "_PTFI_GRS_LL_AMP_3VG_TSX"

# Copy missing files to dest        
for file in files_to_process:
    print("copying {0}".format(file))
    srcfolder = src + "\\" + file[16:19]
    call(["robocopy", srcfolder, dstfolder, os.path.basename(file),"/MT:128"])

# Add new files to mosaic    
for file in files_to_process:
    year = os.path.basename(file)[0:4]       
    dstfolder = dst + "\\" + year + "\\" + year + "_PTFI_GRS_LL_AMP_3VG_TSX"
    new_raster = dstfolder + "\\" + file 
    print(f"Adding {new_raster} to mosaic")
    try:    
        arcpy.management.AddRastersToMosaicDataset(env.workspace, 
                                                   "Raster Dataset", 
                                                   new_raster, 
                                                   "UPDATE_CELL_SIZES", 
                                                   "UPDATE_BOUNDARY", 
                                                   "NO_OVERVIEWS", 
                                                   -1, 
                                                   0, 
                                                   1500, 
                                                   sr, 
                                                   '', 
                                                   "SUBFOLDERS", 
                                                   "EXCLUDE_DUPLICATES",
                                                   "BUILD_PYRAMIDS", 
                                                   "NO_STATISTICS", 
                                                   "NO_THUMBNAILS", '', 
                                                   "NO_FORCE_SPATIAL_REFERENCE", 
                                                   "NO_STATISTICS", None, 
                                                   "NO_PIXEL_CACHE", 
                                                   r"C:\temp\rasterproxies")
    except Exception as e:
                print(e)
                                 
# Process: Select Layer By Attribute
if not files_to_process:
    arcpy.management.SelectLayerByAttribute(mos_dataset, "NEW_SELECTION", """'Acquisition_Date' IS NULL""", None)

    # Calculate aquisition date field
    print("Calculating aquisition date")
    try:    
        arcpy.management.CalculateField(mos_dataset, "Acquisition_Date", '"{0}/{1}/{2}".format(!Name![4:6], !Name![6:8], !Name![0:4])', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    except Exception as e:
        print(e)

# Synchronize mosaic dataset
    print("Synchronizing mosaic dataset")    
    arcpy.management.SynchronizeMosaicDataset(mos_dataset,
                                              '', 
                                              "UPDATE_WITH_NEW_ITEMS", 
                                              "SYNC_ALL", 
                                              "UPDATE_CELL_SIZES",
                                              "UPDATE_BOUNDARY", 
                                              "NO_OVERVIEWS", 
                                              "NO_PYRAMIDS", 
                                              "NO_STATISTICS",
                                              "NO_THUMBNAILS", 
                                              "NO_ITEM_CACHE", 
                                              "REBUILD_RASTER", 
                                              "UPDATE_FIELDS",
                                              "Acquisition_Date;CenterX;CenterY;End_Date;GroupName;Platform;ProductName;Provider;Raster;Shape;Site_Name;Tag;ZOrder",
                                              "UPDATE_EXISTING_ITEMS", 
                                              "IGNORE_BROKEN_ITEMS", 
                                              "OVERWRITE_EXISTING_ITEMS", 
                                              "NO_REFRESH_INFO", 
                                              "NO_STATISTICS")

print("That's all folks!")
        
