# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 07:36:30 2019

@author: smclaugh1

agerrish 8/26/2019:
    Changed Synchronize Mosaic Dataset parameters; SYNC_STALE to SYNC_ALL and SKIP_EXISTING_ITEMS to OVERWRITE_EXISTING_ITEMS
smclaugh1 9/6/2019
    Changed copy functio from shutil to robocopy system call
spabbruw 10/9/2019
    Changed filter method from date to comparing two lists (source files, existing files), added error handeling and changed calculate filed method
spabbruw 3/16/2021
    Modified script to parse new locations and other improvements
smclaugh1 2/2/2022
    Modified script to use Azure source folder
    
This script checks the
\\geospatialnapsa01.file.core.windows.net\insar
folder for new imagery and copies the new files to the

G:\imagery2\Orthoimagery folder.

It then adds the image to the appropriate file geodatabase in the
F:\imagery1\Orthoimagery_GDB folder.

After the file has been added to the source mosaic, the imagery master mosaic is synced
to pick up the new files so it can be servered out via an imagery service.

"""

# Import needed libraries
import arcpy
import re
import glob
import os
from os import path
import time
import datetime
from datetime import timedelta
from datetime import datetime
from subprocess import call

print("loaded modules")

#Alex's Reclass function to parse dates
def Reclass(mystring):
		pattern = re.compile(r'''\d{8,}''')
		if  pattern.search(mystring):
			my_raw_date = pattern.search(mystring)
			d1 = my_raw_date.group(0)
			year = d1[:4]
			month = d1[4:6]
			day = d1[6:8]
			date = time.strftime(year + "/" + month + "/" + day)
			return date
		else:
			pattern = re.compile(r'''(\d+_\d+_\d+_)''')
			if pattern.search(mystring):
				my_raw_date2 = pattern.search(mystring)
				d1 = my_raw_date2.group(0)
				year = d1[:4]
				month = d1[5:7]
				day = d1[8:10]
				date2 = time.strftime(year + "/" + month + "/" + day)
				return date2
			else:
				return None

# Drive where 3vG originals live
srcDrive = r"\\fmi.com\data\PHX\GMX_InSAR\InSAR_from_3vG"

#New source Drive
#srcDrive = r"\\geospatialnapsa01.file.core.windows.net\insar"



# Define destination drive
dst_root = r"G:\imagery2\Orthoimagery"
# Define GBD destination Drive
GDB_path = r"F:\imagery1\Orthoimagery_GDB"

#Today's date for logfile
today = (datetime.now().strftime('%c'))

# Name of sites to be updated
sitenames = [["ABR","ElAbra"],
             ["BAG","Bagdad"],
             ["CHN","Chino"],
             ["CMX","Climax"],
             ["CVE","CerroVerde"],
             ["GRS_HL","PTFI"],
             ["GRS", "PTFI"],
	     ["HEN","Henderson"],
             ["MIA","Miami"],
             ["MOR","Morenci"],
             ["SAM","Safford"],
             ["SAF", "Safford"],
             ["SIE","Sierrita"],
             ["TYR","Tyrone"]
            ]

#Empty list to populate with files to process
images_to_process = []

# Go through the imagery folders and find files like *WebMer.tif
for sitename in sitenames:
    # Define source folder
    sourceFldr = srcDrive + "\\" + sitename[0] + "\\Optical"
    # Define existing folder
    DstFldr = dst_root + "\\" + sitename[1] + "\\ComSat"
    
    # Use glob to make a list of files ending in "WebMer.tif" also searching subfolders recursively   
    files = glob.glob(sourceFldr + r"\**\*WebMer.tif", recursive=True)
    #print(files)
    ### This can be changed to a static year for historical runs ###
    year = datetime.now().strftime("%Y")
    #year = "2022"
    
    #Root destination with year to search for existing
    dstwdate = dst_root + "\\" + sitename[1] + "\\ComSat" + "\\" + year + "\\" + year + "_" + sitename[0] + "_" + "3vG_ComSat"
    
    #Make a list of files in the site existing folder with *WebMer.tif" in the name
    existfiles = glob.glob(dstwdate + r"\*WebMer.tif")
    #print(existfiles)
    existingfiles = []    
    
    #interate through existingfiles to extract basenames
    for existfile in existfiles:
        existingfile = os.path.basename(existfile)
        existingfiles.append(existingfile)
    # list of WebMer.tif files to process if they do not yet exist in the destination folder
    input_path = []
	
    # Iterate through files and find files that do not yet exist in the destination folder      
    for file in files:
        file_last_modified_date = time.strftime('%Y%m%d', time.gmtime(os.path.getmtime(file)))
                
        # Pull the year out of the filename
        pattern = re.compile(r'''\d{8,}''')
		
        # Make full GDB path needed for the add to mosaic command to use if any new files found per site
        in_mosaic_dataset = GDB_path + "\\" + sitename[1] + r"_Imagery.gdb\S_" + sitename[1] + r"_3vG_ComSat"
		
	# Generate the path for the destination to use if any new files found per site
        file_date = pattern.search(file)
        file_date_str = file_date.group(0)[:4]
        dst_path = dst_root + "\\" + sitename[1] + "\\ComSat" + "\\" + file_date_str + "\\" + file_date_str + "_" + sitename[0] + "_" + "3vG_ComSat"
        
        # This will check that the source file is from current year
        if file_date_str == year:
            base_file = os.path.basename(file) 
        
            # Add new files to list to add to mosaic if they are new and write them to the processing list
            if base_file not in existingfiles:
            
                file_name = file.split("\\")[-1:]
                raster_name = dst_path + "\\" + file_name[0]

                #Copy new imagery to Imagery folder
                print("{0} begin copying: {1}".format((datetime.now().strftime('%c')), file_name[0]))
                call(["robocopy", sourceFldr, dst_path, file_name[0],"/MT:128"])
            
                # Add file to input path for processing
                sitename0 = sitename[0]
                sitename1 = sitename[1]
                newfile = dst_path + "\\" + file_name[0]
                images_to_process.append([newfile, in_mosaic_dataset,sitename0,sitename1])

print("Getting ready to add these items to the mosaic datasets: {0}".format(images_to_process))
    
# Add new rasters to mosaic
for image in images_to_process:
    print("{0} For site {3} adding {1} to {2}".format((datetime.now().strftime('%c')), image[0], image[1], image[2]))
    
    #exception handeling starts here
    try:    
        arcpy.AddRastersToMosaicDataset_management(image[1], 
        					   "RASTER DATASET", 
        					   image[0], 
        					   "UPDATE_CELL_SIZES", 
                               "UPDATE_BOUNDARY", 
                              "NO_OVERVIEWS", 
                               -1, 
                               0, 
                               1500, 
                               '',
                               '', 
                               "SUBFOLDERS", 
                               "EXCLUDE_DUPLICATES", 
                               "BUILD_PYRAMIDS", 
                               "NO_STATISTICS", 
                               "NO_THUMBNAILS", 
                               '', 
                               "NO_FORCE_SPATIAL_REFERENCE",
                               "NO_STATISTICS", 
                               None, 
                               "NO_PIXEL_CACHE", 
                               r"C:\temp\rasterproxies")
        
        prov = "3vG"
        plat = "ComSat"
        
        # Process: Select Layer By Attribute
        arcpy.SelectLayerByAttribute_management(image[1], selection_type="NEW_SELECTION", where_clause="Site_Name IS NULL And Acquisition_Date IS NULL")
    	
        # Process: Calculate Field (Update Site Name, Provider, Platform, Acquisition Date)
        arcpy.management.CalculateField(image[1], "Site_Name", """image[3]""", "PYTHON3", '')
        arcpy.management.CalculateField(image[1], "Provider", """prov""", "PYTHON3", '')
        arcpy.management.CalculateField(image[1], "Platform", """plat""", "PYTHON3", '')
        arcpy.management.CalculateField(image[1], "Acquisition_Date", """Reclass(!Name!)""", "PYTHON3", '') 
            
    #exception handeling goes here if failure    
    except Exception as e:
        print("{4} Failed to process = {0}, {1}, {2}, {3}".format(image[0], image[1], image[2], image[3], e))

print("{0} Done adding files to mosaics.".format((datetime.now().strftime('%c'))))
    
# Syncronize the All_Site_Imagery Master
if images_to_process:

    print("{0} syncing mosaic datasets".format((datetime.now().strftime('%c'))))

    
    arcpy.management.SynchronizeMosaicDataset(r"F:\imagery1\Orthoimagery_GDB\All_Site_Imagery.gdb\D_All_Site_Imagery_3vG_Comsat",
                                               '', "UPDATE_WITH_NEW_ITEMS", "SYNC_ALL", "UPDATE_CELL_SIZES",
                                               "UPDATE_BOUNDARY", "NO_OVERVIEWS", "NO_PYRAMIDS", "NO_STATISTICS",
                                              "NO_THUMBNAILS", "NO_ITEM_CACHE", "REBUILD_RASTER", "UPDATE_FIELDS",
                                               "Acquisition_Date;CenterX;CenterY;End_Date;GroupName;Platform;ProductName;Provider;Raster;Shape;Site_Name;Tag;ZOrder",
                                               "UPDATE_EXISTING_ITEMS", "IGNORE_BROKEN_ITEMS", "OVERWRITE_EXISTING_ITEMS", "NO_REFRESH_INFO", "NO_STATISTICS")

print("{0} Finished processing rasters.".format((datetime.now().strftime('%c')))) 

