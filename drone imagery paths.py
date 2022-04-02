# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 14:27:19 2022

@author: admin-gis-prdp02
"""
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
#src = r"\\fmi.com\data\PHX\GMX_InSAR\InSAR_from_3vG\GRS_LL\Amplitudes"

src = r"G:\Imagery_Server_Inbox"
dst = r"G:\Imagery2\Orthoimagery"
year = str(datetime.datetime.now().year)
srcfiles=[]
dstfiles=[]
file = ""

# Get files in src folder
for srcpath in glob.glob(src +  "/**/*.tif*", recursive=True):
    file = os.path.basename(srcpath)
    print(srcpath)
    #if int(file[0:4]) > 2020:
        #srcfiles.append(file)
#%%
# Get files in dest folder    
for dstpath in glob.glob(dst +  "/**/*.tif*", recursive=True):
    if "aerial" in dstpath:
        print(dstpath)
    #file = os.path.basename(dstpath)
    #dstfiles.append(file)
#%%
# Compare file lists    
files_to_process =[]
for file in srcfiles:
    if file not in dstfiles:
        files_to_process.append(file)
        #year = os.path.basename(file)[0:4]       
dstfolder = dst + "\\" + year + "\\" + year + "_PTFI_GRS_LL_AMP_3VG_TSX"