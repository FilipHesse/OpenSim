import opensim as osim
import numpy as np
import os

dir_path = r"C:\Users\Filip Hesse\OneDrive\Dokumente\Studium\UNIGE\Year2\Thesis\OpenSim\Adafuse"                 # Change the path to the location of you openSim project

generic_MM_Path = os.path.join(dir_path, "Rajagopal2015_adafuse_21kpts.osim")      # Path to the Generic Musculoskeletal Model
XML_generic_ST_path = os.path.join(dir_path,'scaling.xml')                         # Path to the generic Scale Tool XML file
XML_markers_path = os.path.join(dir_path,'markers.xml')                            # Path to the markers XML file
TRC_file = r"C:\Users\Filip Hesse\OneDrive\Dokumente\Studium\UNIGE\Year2\Thesis\output_media_big_for_github\adafuse\3_trc_files\S14_Normal_00_01_825-00_04_284_j3d_AdaFuse.trc"                                           # Path to the .trc file that contain the marker data

XML_ST_file = os.path.join(dir_path,'output\\scaleToolSubject.xml')                             # Path to the subject Scale Tool XML file that will be created
XML_SF_file = os.path.join(dir_path,'output\\scaleFactorSubject.xml')                           # Path to the subject Scale Factor file that will be created
scaled_MM_path = os.path.join(dir_path,'output\\Subject.osim')                        # Path to the subject Musculoskeletal Model that will be created with the model scaler
scaled_MM_path2 = os.path.join(dir_path,'output\\SubjectMoved.osim')                  # Path to the subject Musculoskeletal Model that will be created with the marker placer
XML_markers_path_move = os.path.join(dir_path,'output\\markersMoved.xml')                       # Path to the markers XML file created with the marker placer

# Create a list of Marker Pair Set for each body
markerList = np.array(
['rsho', 'lsho', 'relb', 'rwri', 'lelb', 'lwri','rkne', 'rhee', 
'rtoe', 'lkne', 'lhee', 'ltoe', 'rhip', 'lhip', 
'rfoo', 'lfoo', 'neck', 'belly', 'root', 'nose', 'head'])

markerPairList =  np.array([['rhip', 'lhip'],
                  ['rhip', 'rkne'], ['rkne', 'rhee'],
                  ['rhip', 'rkne'], ['rtoe', 'rhee'], ['rtoe', 'rhee'], ['rtoe', 'rhee'],
                  ['lhip', 'lkne'], ['lkne', 'lhee'],
                  ['lhip', 'lkne'], ['ltoe', 'lhee'], ['ltoe', 'lhee'], ['ltoe', 'lhee'],
                  ['rsho', 'lsho'], ['nose', 'root'],
                  ['relb', 'rsho'], ['relb', 'rwri'], ['relb', 'rwri'],
                  ['lelb', 'lsho'], ['lelb', 'lwri'], ['lelb', 'lwri']])

bodyNames =  np.array([['pelvis'],
             ['femur_r'], ['tibia_r'],
             ['patella_r'], ['talus_r'], ['calcn_r'], ['toes_r'],
             ['femur_l'], ['tibia_l'],
             ['patella_l'], ['talus_l'], ['calcn_l'], ['toes_l'],
             ['torso'], ['torso'],
             ['humerus_r'], ['ulna_r'], ['radius_r'],
             ['humerus_l'], ['ulna_l'], ['radius_l']])

nBody = bodyNames.shape[0]

# The first step is to create an XML file with all the information used to scale the model

# Load the generic musculoskeletal model
osimModel = osim.Model(generic_MM_Path)
state = osimModel.initSystem()

# Add a marker set to the model
markerSet = osim.MarkerSet(XML_markers_path)
osimModel.set_MarkerSet(markerSet)
#osimModel.replaceMarkerSet(state, markerSet)
state = osimModel.initSystem()

# Get the marker data from a .trc file
markerData = osim.MarkerData(TRC_file)
initial_time = markerData.getStartFrameTime()
final_time = markerData.getLastFrameTime()
TimeArray = osim.ArrayDouble()                                                 # Time range
TimeArray.set(0,initial_time)
TimeArray.set(1,initial_time)       # Work with one frame (initial) only! 

# Scale Tool
scaleTool = osim.ScaleTool(XML_generic_ST_path)
scaleTool.setName('Subject')                                                   # Name of the subject
scaleTool.setSubjectMass(70)                                                   # Mass of the subject
scaleTool.setSubjectHeight(-1)                                                 # Only for information (not used by scaling)
scaleTool.setSubjectAge(-1)                                                    # Only for information (not used by scaling)

# Generic Model Maker
scaleTool.getGenericModelMaker().setModelFileName('Rajagopal2015.osim')
scaleTool.getGenericModelMaker().setMarkerSetFileName(XML_markers_path)

# Model Scaler
scaleTool.getModelScaler().setApply(True)
scaleTool.getModelScaler().setScalingOrder(osim.ArrayStr('measurements', 1))
scaleTool.getModelScaler().setMarkerFileName(TRC_file)                          
scaleTool.getModelScaler().setTimeRange(TimeArray)
scaleTool.getModelScaler().setPreserveMassDist(True)
scaleTool.getModelScaler().setOutputModelFileName(scaled_MM_path)
scaleTool.getModelScaler().setOutputScaleFileName(XML_SF_file)

# The scale factor information concern the pair of marker that will be used
# to scale each body in your model to make it more specific to your subject.
# The scale factor are computed with the distance the virtual markers and between your experimental markers

# Create a Marker Pair Set fo each body
measurementTemp = osim.Measurement()
bodyScaleTemp = osim.BodyScale()
markerPairTemp = osim.MarkerPair()

for i in range(0, nBody):

    # Create a Marker Pair Set
    markerPair = markerPairTemp.clone()
    markerPair.setMarkerName(0, markerPairList[i][0])
    markerPair.setMarkerName(1, markerPairList[i][1])

    # Create a Body Scale Set
    bodyScale = bodyScaleTemp.clone()
    bodyScale.setName(bodyNames[i][0]) # Name of the body
    bodyScale.setAxisNames(osim.ArrayStr('X Y Z', 1))
    
    # Create a measurement
    measurement = measurementTemp.clone()
    measurement.setApply(True)
    measurement.getBodyScaleSet().adoptAndAppend(bodyScale)
    measurement.getMarkerPairSet().adoptAndAppend(markerPair)
    measurement.setName(bodyNames[i][0]) # Whatever name you want(Usually I set the same name as the body)
    
    # Add the measurement to the Model Scaler
    scaleTool.getModelScaler().addMeasurement(measurement)

# Create the subject Scale Tool XML file
#scaleTool.setPrintResultFiles(True)
scaleTool.printToXML(XML_ST_file)
print('XML files : ' +  XML_ST_file + ' created')

# Launch the scale tool again with the new XML file and then scale the
# generic musculoskeletal model
scaleTool = osim.ScaleTool(XML_ST_file)

# Scale the model
scaleTool.getModelScaler().processModel(osimModel)
print('Scaled Musculoskeletal : ' + scaled_MM_path + ' created')

# In this part, we will use the previous XML file created and update it
# with the MarkerPlacer tool to Adjust the position of the marker on the
# scaled musculoskeletal model

# Load the scaled musculoskeletal model
osimModel = osim.Model(scaled_MM_path)
state = osimModel.initSystem()

# Add a marker set to the model
markerSet = osim.MarkerSet(XML_markers_path)
osimModel.set_MarkerSet(markerSet)
#osimModel.replaceMarkerSet(state, markerSet)
state = osimModel.initSystem()

# Launch the scale tool
scaleTool = osim.ScaleTool(XML_ST_file)

# Get the marker data from a.trc file
markerData = osim.MarkerData(TRC_file)
initial_time = markerData.getStartFrameTime()
final_time = markerData.getLastFrameTime()
TimeArray = osim.ArrayDouble() # Time range
TimeArray.set(0, initial_time)
TimeArray.set(1, initial_time+0.01)        # Work with one frame (initial) only! 

# The static pose weights will be used to adjust the markers position in 
# the model from a static pose. The weights of the markers depend of the
# confidence you have on its position.In this example, all marker weight
# are fixed to one.

scaleTool.getMarkerPlacer().setApply(True) # Ajustement placement de marqueurs(true or false)
scaleTool.getMarkerPlacer().setStaticPoseFileName(TRC_file) # trc files for adjustements(usually the same as static)
scaleTool.getMarkerPlacer().setTimeRange(TimeArray) # Time range
scaleTool.getMarkerPlacer().setOutputModelFileName(scaled_MM_path2)
scaleTool.getMarkerPlacer().setOutputMarkerFileName(XML_markers_path_move)
scaleTool.getMarkerPlacer().setMaxMarkerMovement(-1.0)

measurementTemp = osim.Measurement()
ikMarkerTaskTemp = osim.IKMarkerTask()

for i in range(0, markerList.shape[0]):

    ikMarkerTask = ikMarkerTaskTemp.clone()

    ikMarkerTask.setName(markerList[i]) # Name of the markers
    ikMarkerTask.setApply(True)
    ikMarkerTask.setWeight(1)

    scaleTool.getMarkerPlacer().getIKTaskSet().adoptAndAppend(ikMarkerTask)

# Create the subject Scale Tool XML file
scaleTool.printToXML(XML_ST_file)
print('XML files : ' + XML_ST_file + ' created')

# Launch the ScaleTool again
scaleTool = osim.ScaleTool(XML_ST_file)
scaleTool.getMarkerPlacer().processModel(osimModel)
print('Adjusted markers on the musculoskeletal done')
print('Adjusted markers XML file: ' +  XML_markers_path_move + ' created')

# Display the Scale Factor after the scaling process
osimModel = osim.Model(scaled_MM_path2)
state = osimModel.initSystem()

nBody = osimModel.getBodySet().getSize() # Number of Body

bodyNames = []
scaleFactors = []
# Display scale factors
for i in range(0, nBody):
    break
    ScaleFactor = osim.Vec3(0, 0, 0)
    body_set = osimModel.getBodySet()#.getScaleFactors(ScaleFactor)
    
    bodyNames.append(osimModel.getBodySet().get(i).getName())
    scaleFactors.append([ScaleFactor.get(0), ScaleFactor.get(1), ScaleFactor.get(2)])

    if (any(i == t for t in [0, 1, 7, 13, 14, 16, 18, 20, 22])):
        tab = '\t\t'
    else:
        tab = '\t'

    print('Scale factors of ' +  str(bodyNames[i]) + tab + ' - X: ' +  "{:.3f}".format(scaleFactors[i][0])) + '\t\t - Y: ' + "{:.3f}".format(scaleFactors[i][1]) + '\t\t - Z: ' + "{:.3f}".format(scaleFactors[i][2])