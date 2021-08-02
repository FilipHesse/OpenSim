import opensim as osim
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

# DataBase
dir_path = r"C:\Users\Filip Hesse\OneDrive\Dokumente\Studium\UNIGE\Year2\Thesis\OpenSim\Adafuse"  

scaled_MM_Moved_path = os.path.join(dir_path, 'output\\SubjectMoved.osim')  # Path to the subject Musculoskeletal Model that will be created

#TRC_files = np.array(['TRC\\Walk_Mkrs.trc', 'TRC\\Walk_Mkrs2.trc', 'TRC\\Walk_Mkrs3.trc'])
TRC_file = r"C:\Users\Filip Hesse\OneDrive\Dokumente\Studium\UNIGE\Year2\Thesis\output_media_big_for_github\adafuse\3_trc_files\S14_Normal_00_01_825-00_04_284_j3d_AdaFuse.trc"                                           # Path to the .trc file that contain the marker data


XML_generic_IK_path = os.path.join(dir_path, 'IK.xml') # Path to the generic IK XML file

markerList = np.array(
['rsho', 'lsho', 'relb', 'rwri', 'lelb', 'lwri','rkne', 'rhee', 
'rtoe', 'lkne', 'lhee', 'ltoe', 'rhip', 'lhip', 
'rfoo', 'lfoo', 'neck', 'belly', 'root', 'nose', 'head'])

markerWeight = np.ones_like(markerList, dtype=np.double)

# Launch the musculoskeletal model
osimModel = osim.Model(scaled_MM_Moved_path)
state = osimModel.initSystem()



path, filename = os.path.split(TRC_file)
filename, ext = os.path.splitext(filename)

MOT_file = os.path.join(dir_path, 'output\\' + filename + '.mot')                                # Path to the output .MOT file that will be created and contain the IK results
XML_IK_file = os.path.join(dir_path, 'output\\' + filename + '_IK.xml' )                        # Path to the IK XML file that will be created

# Marker Data
markerData = osim.MarkerData(TRC_file)
initial_time = markerData.getStartFrameTime()
final_time = markerData.getLastFrameTime()

# Set the IK tool
ikTool = osim.InverseKinematicsTool(XML_generic_IK_path)
ikTool.setModel(osimModel)
ikTool.setName(filename + ext)
ikTool.setMarkerDataFileName(TRC_file)
ikTool.setStartTime(initial_time)
ikTool.setEndTime(final_time)
ikTool.setOutputMotionFileName(MOT_file)

# Set the ikTool with the MarkerTask
for j in range(0, markerList.shape[0]):
    ikMarkerTask = osim.IKMarkerTask()
    ikMarkerTask.setName(markerList[j])
    ikMarkerTask.setApply(True)
    ikMarkerTask.setWeight(markerWeight[j])
    ikTool.getIKTaskSet().adoptAndAppend(ikMarkerTask)

# Create the IK XML file
ikTool.printToXML(XML_IK_file)
ikTool.run()
