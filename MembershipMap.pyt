# Python Toolbox used to create membership maps
# Allows user selection of location, input data and ouput maps types

import arcpy
import os
import sys
from arcpy.sa import *
import time

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Membership Map"
        self.alias = "MembershipMap"

        # List of tool classes associated with this toolbox

        self.tools = [MapTool]

class MapTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Map membership locations"
        self.description = "n/a"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        p0 = arcpy.Parameter(
            displayName="Study Area boundaries",
            name="SAboundary",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        p0.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData\Inputs.gdb', 'District_borough_unitary_region')

        p1 = arcpy.Parameter(
           displayName="Select Study Area",
            name="SAreaSQL",
            datatype="GPSQLExpression",
            parameterType="Required",
            direction="Input")
        p1.value = "NAME = 'County Durham'"
        p1.parameterDependencies = [p0.name]

        p2 = arcpy.Parameter(
            displayName="Scratch",
            name="Scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p2.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'3 OutputData\Scratch.gdb')

        p3 = arcpy.Parameter(
            displayName="Code Point Postcodes",
            name="CodePoint",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p3.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData\Inputs.gdb', 'CodePoint')

        p4 = arcpy.Parameter(
           displayName="Set field in CodePoint with Postcodes",
            name="ValuesF",
            datatype="Field",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p4.value = 'Poscode'
        p4.parameterDependencies = [p3.name]

        p5 = arcpy.Parameter(
           displayName="Data table with memberships",
            name="MembersT",
            datatype="DETable",
            parameterType="Required",
            direction="Input")
        p5.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData', 'Memberships.csv')

        p6 = arcpy.Parameter(
           displayName="Set field in memberships table with Postcodes",
            name="PostF",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        p6.value = 'Postcode'
        p6.parameterDependencies = [p5.name]

        p7 = arcpy.Parameter(
            displayName="Outputs",
            name="Outputs",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p7.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'3 OutputData\Outputs.gdb')

        p8 = arcpy.Parameter(
            displayName="Open and view data in ArcMap when analysis is complete?",
            name="Aview1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p8.value = 'true'

        p9 = arcpy.Parameter(
            displayName="Set buffer distance around Study Area",
            name="Buffer",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        p9.value = 10000

        p10 = arcpy.Parameter(
            displayName="Use County or region based Study Area?",
            name="Study1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p10.value = 'true'

        p11 = arcpy.Parameter(
            displayName="Set alternative Study Area boundary from file",
            name="UserStudy",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p11.value = 'false'

        p12 = arcpy.Parameter(
            displayName="Select alternative Study Area from file",
            name="AltArea",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")

        p13 = arcpy.Parameter(
            displayName="Indicators",
            name="Indicators",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p13.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'3 OutputData\Indicators.gdb')

        p14 = arcpy.Parameter(
            displayName="Set grid cell size (meters)",
            name="Grid",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        p14.value = 2000

        p15 = arcpy.Parameter(
            displayName="Include Reserve location points?",
            name="Reserves",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p15.value = 'false'

        p16 = arcpy.Parameter(
           displayName="Reserve points data",
            name="ReservesT",
            datatype="DETable",
            parameterType="Optional",
            direction="Input")
        p16.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData', 'Reserves.csv')

        p17 = arcpy.Parameter(
            displayName="Census areas",
            name="Census",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p17.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData\Inputs.gdb', 'OA_2011_GB')

        p18 = arcpy.Parameter(
            displayName="Create PDFs?",
            name="PDFs",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p18.value = 'false'



        return [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9, p10, p11, p12, p13,p14,p15,p16,p17,p18]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

       # parameter list

        SAboundary           = parameters[0].valueAsText
        SAreaSQL             = parameters[1].valueAsText
        Scratch              = parameters[2].valueAsText
        CodePoint            = parameters[3].valueAsText
        PostcodeM            = parameters[4].valueAsText
        MembersT             = parameters[5].valueAsText
        PostF                = parameters[6].valueAsText
        Outputs              = parameters[7].valueAsText
        Aview1               = parameters[8].valueAsText
        Buffer               = parameters[9].valueAsText
        Stufy1               = parameters[10].valueAsText
        UserStudy            = parameters[11].valueAsText
        AltArea              = parameters[12].valueAsText
        Indicators           = parameters[13].valueAsText
        Grids                = parameters[14].valueAsText

        Reserves             = parameters[15].valueAsText
        ReservesT            = parameters[16].valueAsText
        Census               = parameters[17].valueAsText
        PDFs                 = parameters[18].valueAsText

       # local parameter list

        SA_lyr               = "SA_lyr"
        Code_lyr             = "Code_lyr"
        Members_lyr          = "Members_lyr"
        MembersOut           = os.path.join(Outputs,"Members")
        MembershipsOut       = os.path.join(Outputs,"Memberships")
        GridMships           = os.path.join(Outputs,"Number_Memberships")
        GridMembers          = os.path.join(Outputs,"Number_Members")
        FNScrSDOut           = os.path.join(Indicators, "Mship_Zscr_SD_IndC")
        MScrSDOut            = os.path.join(Indicators, "Mbrs_Zscr_SD_IndC")
        PcntScrSDOut         = os.path.join(Indicators, "Pcnt_Zscr_SD_IndC")
        Census_lyr           = "Census_lyr"
        PopnOut              = os.path.join(Outputs,"Population")
        DTM1                 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'2 InputData\Inputs.gdb', 'DTM1000')
        PDFloctn             = os.path.join(os.path.dirname(os.path.dirname(__file__)),'4 PDFs')

        # set overwrite and scratch workspace

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = Scratch
        arcpy.Resample_management(DTM1, "snap", Grids)
        arcpy.env.snapRaster = "snap"

        spatial_ref = arcpy.Describe(Census).spatialReference
        arcpy.env.outputCoordinateSystem = spatial_ref

        # begin messages for user

        arcpy.AddMessage(" ")
        messages.addMessage("    Preparing data for analysis")

        Tresult = arcpy.GetCount_management(MembersT)
        Tcount = int(Tresult.getOutput(0))

        messages.addMessage("    Memberships input data has  " + str(Tcount) + "  records")


        arcpy.MakeFeatureLayer_management(SAboundary, SA_lyr, SAreaSQL)
        arcpy.CopyFeatures_management(SA_lyr, "StudyArea_MX")

        if UserStudy == 'true':
          arcpy.CopyFeatures_management(AltArea, "StudyArea_MX")

        else:
          arcpy.AddMessage(" ")

        BfrInput = "StudyArea_MX"
        BfrOut = "SA_buffer_MX"
        distance = Buffer
        sideType = "FULL"
        endType = "ROUND"
        dissolveType = "NONE"
        dissolveField = ""

        messages.addMessage("    Applying " + str(Buffer) + " m buffer to Study Area")

        arcpy.Buffer_analysis(BfrInput, BfrOut, distance, sideType, endType, dissolveType, dissolveField)


        messages.addMessage("    Selecting Post Codes within Study Area Buffer")

        arcpy.MakeFeatureLayer_management(CodePoint, Code_lyr)
        arcpy.SelectLayerByLocation_management (Code_lyr, "INTERSECT", "SA_buffer_MX")
        arcpy.CopyFeatures_management(Code_lyr, "in_memory\LocCodes_MX")
        arcpy.CopyRows_management(MembersT, "in_memory\MembersCopy_MX")
        TM = arcpy.GetCount_management("in_memory\LocCodes_MX")
        Tc = int(TM.getOutput(0))

        messages.addMessage("    There are   " + str(Tc) + "  Post Codes in the Study Area Buffer")



        inFeatures = "in_memory\MembersCopy_MX"
        joinFieldIn = PostF
        joinFieldJT = PostcodeM
        joinTable = "in_memory\LocCodes_MX"
        fieldList = ["easting", "northing"]
        arcpy.JoinField_management (inFeatures, joinFieldIn, joinTable, joinFieldJT, fieldList)

        messages.addMessage("    Joining location grid ref to membership postcodes")


        arcpy.MakeTableView_management(inFeatures, "m_view")

        in_Table = "m_view"
        x_coords = "easting"
        y_coords = "northing"
        z_coords = ""
        out_Layer = "members_view"

        # Set the spatial reference
        spRef = spatial_ref

        # Make the XY event layer...
        arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, spRef, z_coords)
        arcpy.SelectLayerByAttribute_management (out_Layer, "NEW_SELECTION", ' "easting" >= 0 ')
        arcpy.CopyFeatures_management(out_Layer, "MembersPoints")
        TP = arcpy.GetCount_management("MembersPoints")
        TPt = int(TP.getOutput(0))

        messages.addMessage("    There are  " + str(TPt) + "  matching membership records in the Study Area Buffer")


        messages.addMessage("    Selecting Census Areas (OA, DZ) within Study Area Buffer")

        arcpy.MakeFeatureLayer_management(Census, Census_lyr)
        arcpy.SelectLayerByLocation_management (Census_lyr, "INTERSECT", "SA_buffer_MX")
        arcpy.CopyFeatures_management(Census_lyr, "in_memory\LocCensus_MX")

        Tcc = arcpy.GetCount_management("in_memory\LocCensus_MX")
        Tcct = int(Tcc.getOutput(0))

        messages.addMessage("    There are  " + str(Tcct) + "  Census Areas (OA, DZ) intersecting the Study Area Buffer")


        # move to in memory
        arcpy.CopyFeatures_management("MembersPoints", "in_memory\Loc_MX")

        messages.addMessage("    Joining Census Areas (OA, DZ) data to local Post Codes points")

        target_features = "in_memory\Loc_MX"
        join_features = "in_memory\LocCensus_MX"
        out_feature_class = "LocDataP_MX"

        arcpy.SpatialJoin_analysis(target_features, join_features, out_feature_class)

        TD = arcpy.GetCount_management("LocDataP_MX")
        TDct = int(TD.getOutput(0))

        messages.addMessage("    There are  " + str(TDct) + "  matching memberships with joined Cenus Areas (OA, DZ) data")

        # calculate how many postcodes points per Census Area

        messages.addMessage("    Calculate Post Code point per Census Area")

        inTable = "LocDataP_MX"
        outStatsTable = "stats_out_MX"
        statsFields = [["Nm1", "SUM"]]
        caseField = "OAC"

        arcpy.Statistics_analysis(inTable, outStatsTable, statsFields, caseField)

        # Join the data field back to the point data

        arcpy.CopyFeatures_management("LocDataP_MX", "in_memory\LocD")
        inFeatures = "in_memory\LocD"
        joinField = "OAC"
        joinTable = "stats_out_MX"
        fieldList = ["SUM_Nm1"]

        messages.addMessage("    Calculate  local population sizes")

        arcpy.JoinField_management (inFeatures, joinField, joinTable, joinField, fieldList)

        # add and calculate popn fields

        intabepr = "in_memory\LocD"
        fieldName1 = "PopnX"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""
        expression1 = "!all_people_x!  / !SUM_Nm1! "

        arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.CalculateField_management(intabepr, fieldName1, expression1 , "PYTHON_9.3")


        arcpy.CopyFeatures_management("in_memory\LocD", MembersOut)

        intabepr = MembersOut
        fieldName1 = "Memberships"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""

        arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.CalculateField_management(intabepr, fieldName1, 1 , "PYTHON_9.3")

        result = arcpy.GetCount_management(MembersOut)
        Mcount = int(result.getOutput(0))


        inFeatures = MembersOut
        valField = "Memberships"
        outRaster = GridMships
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids

        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of memberships")

        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        MaxD            = arcpy.GetRasterProperties_management(GridMships,property_type="MAXIMUM")

         # standardising variables

        messages.addMessage("     : Standardising data variables")

        FNvar = GridMships

        min1            = arcpy.GetRasterProperties_management(FNvar,property_type="MINIMUM")
        max1            = arcpy.GetRasterProperties_management(FNvar,property_type="MAXIMUM")
        mean1           = arcpy.GetRasterProperties_management(FNvar,property_type="MEAN")
        std1           = arcpy.GetRasterProperties_management(FNvar,property_type="STD")
        vmin1           = min1.getOutput(0)
        vmax1           = max1.getOutput(0)
        vmean1          = mean1.getOutput(0)
        vstd1           = std1.getOutput(0)
        vmin1f          = float(vmin1)
        vmax1f          = float(vmax1)
        vmean1f         = float(vmean1)
        vstd1f          = float(vstd1)
        VR3             = vmax1f - vmin1f
        VR4              = (99 / VR3)
        VR5              = Minus(FNvar, vmax1f)
        VR6              = Times(VR5, VR4)
        VR7              = Plus(VR6, 99)

        VarSD1             = Minus(FNvar, vmean1f)
        VarSD2             = Divide(VarSD1, vstd1f)
        VarSD2.save(os.path.join(Indicators, "Mship_Zscore_IndC"))

        VarSD3 = Reclassify(VarSD2, "Value", "-100 -2  30; -2 -1 20; -1 -0.5 15; -0.5  -0.001 10; -0.001 0.001 5; 0.01 0.5 4; 0.5 1 3; 1 2 2; 2 100 1", "NODATA")
        VarSD3.save(FNScrSDOut)

        intabepr = FNScrSDOut
        fieldName1 = "Category"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""

        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        expression = "Reclass ( !Category!, !Value!)"
        codeblock = """def Reclass (Category, Value):
  if (Value == 30) :
    return '< -3 SD'
  elif (Value == 20) :
   return '- 2 SD'
  elif (Value == 15) :
    return '-1 SD'
  elif (Value == 10) :
    return '- 0.5 SD'
  elif (Value == 5) :
    return 'Mean'
  elif (Value == 4) :
    return '+ 0.5 SD'
  elif (Value == 3) :
    return '+ 1 SD'
  elif (Value == 2) :
    return '+ 2 SD'
  elif (Value == 1) :
    return '> + 3 SD'"""

        arcpy.CalculateField_management(intabepr, fieldName1, expression, "PYTHON_9.3", codeblock)









        inFeatures = MembersOut
        valField = "Members"
        outRaster = GridMembers
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids

        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of members")

        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        MMaxD            = arcpy.GetRasterProperties_management(GridMembers,property_type="MAXIMUM")

         # standardising variables

        messages.addMessage("     : Standardising data variables")

        FNvar = GridMembers

        min1            = arcpy.GetRasterProperties_management(FNvar,property_type="MINIMUM")
        max1            = arcpy.GetRasterProperties_management(FNvar,property_type="MAXIMUM")
        mean1           = arcpy.GetRasterProperties_management(FNvar,property_type="MEAN")
        std1           = arcpy.GetRasterProperties_management(FNvar,property_type="STD")
        vmin1           = min1.getOutput(0)
        vmax1           = max1.getOutput(0)
        vmean1          = mean1.getOutput(0)
        vstd1           = std1.getOutput(0)
        vmin1f          = float(vmin1)
        vmax1f          = float(vmax1)
        vmean1f         = float(vmean1)
        vstd1f          = float(vstd1)
        VR3             = vmax1f - vmin1f
        VR4              = (99 / VR3)
        VR5              = Minus(FNvar, vmax1f)
        VR6              = Times(VR5, VR4)
        VR7              = Plus(VR6, 99)

        VarSD1             = Minus(FNvar, vmean1f)
        VarSD2             = Divide(VarSD1, vstd1f)
        VarSD2.save(os.path.join(Indicators, "Mbrs_Zscore_IndC"))

        VarSD3 = Reclassify(VarSD2, "Value", "-100 -2  30; -2 -1 20; -1 -0.5 15; -0.5  -0.001 10; -0.001 0.001 5; 0.01 0.5 4; 0.5 1 3; 1 2 2; 2 100 1", "NODATA")
        VarSD3.save(MScrSDOut)

        intabepr = MScrSDOut
        fieldName1 = "Category"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""

        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        expression = "Reclass ( !Category!, !Value!)"
        codeblock = """def Reclass (Category, Value):
  if (Value == 30) :
    return '< -3 SD'
  elif (Value == 20) :
   return '- 2 SD'
  elif (Value == 15) :
    return '-1 SD'
  elif (Value == 10) :
    return '- 0.5 SD'
  elif (Value == 5) :
    return 'Mean'
  elif (Value == 4) :
    return '+ 0.5 SD'
  elif (Value == 3) :
    return '+ 1 SD'
  elif (Value == 2) :
    return '+ 2 SD'
  elif (Value == 1) :
    return '> + 3 SD'"""

        arcpy.CalculateField_management(intabepr, fieldName1, expression, "PYTHON_9.3", codeblock)


        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of population size")

        inFeatures = MembersOut
        valField = "PopnX"
        outRaster = PopnOut
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids

        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        VarP1              = Divide(GridMembers, PopnOut)
        VarP2              = Times (VarP1, 100)
        VarP2.save(os.path.join(Outputs, "Percent"))


        messages.addMessage("     : Standardising Membership percent data variables")

        FNvar = VarP2

        Pmax1           = arcpy.GetRasterProperties_management(FNvar,property_type="MAXIMUM")
        Pmean1          = arcpy.GetRasterProperties_management(FNvar,property_type="MEAN")
        Pstd1           = arcpy.GetRasterProperties_management(FNvar,property_type="STD")
        Pvmax1           = Pmax1.getOutput(0)
        Pvmean1          = Pmean1.getOutput(0)
        Pvstd1           = Pstd1.getOutput(0)

        vmax1f          = float(Pvmax1)
        vmean1f         = float(Pvmean1)
        vstd1f          = float(Pvstd1)

        VarPNT1            = Minus(FNvar, vmean1f)
        VarPNT2            = Divide(VarPNT1, vstd1f)
        VarPNT2.save(os.path.join(Indicators, "Pcnt_Zscore_IndC"))

        VarPNT3 = Reclassify(VarPNT2, "Value", "-100 -2  30; -2 -1 20; -1 -0.5 15; -0.5  -0.001 10; -0.001 0.001 5; 0.01 0.5 4; 0.5 1 3; 1 2 2; 2 100 1", "NODATA")
        VarPNT3.save(PcntScrSDOut)

        intabepr = PcntScrSDOut
        fieldName1 = "Category"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""

        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        expression = "Reclass ( !Category!, !Value!)"
        codeblock = """def Reclass (Category, Value):
  if (Value == 30) :
    return '< -3 SD'
  elif (Value == 20) :
   return '- 2 SD'
  elif (Value == 15) :
    return '-1 SD'
  elif (Value == 10) :
    return '- 0.5 SD'
  elif (Value == 5) :
    return 'Mean'
  elif (Value == 4) :
    return '+ 0.5 SD'
  elif (Value == 3) :
    return '+ 1 SD'
  elif (Value == 2) :
    return '+ 2 SD'
  elif (Value == 1) :
    return '> + 3 SD'"""


        arcpy.CalculateField_management(intabepr, fieldName1, expression, "PYTHON_9.3", codeblock)




        map_file1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'6 Templates', 'Type.mxd')
        mxd1 = arcpy.mapping.MapDocument(map_file1)
        df = arcpy.mapping.ListDataFrames(mxd1, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd1, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd1.save()

        # Loop through each text element in the map document
        for textElement in arcpy.mapping.ListLayoutElements(mxd1, "TEXT_ELEMENT"):

            # Check if the text element contains the out of date text
            if textElement.text == "Text1":

            # If out of date text is found, replace it with the new text
                textElement.text = ("Memberships = " + str(Mcount) + " records" )

            # Check if the text element contains the out of date text
            if textElement.text == "Text0":

            # If out of date text is found, replace it with the new text
                textElement.text = (str(Tcount) + " records" )

        mxd1.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '1 Type of membership.mxd'))


        map_file2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'6 Templates', 'Density.mxd')
        mxd2 = arcpy.mapping.MapDocument(map_file2)
        df = arcpy.mapping.ListDataFrames(mxd2, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd2, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd2.save()

        # Loop through each text element in the map document
        for textElement in arcpy.mapping.ListLayoutElements(mxd2, "TEXT_ELEMENT"):

            # Check if the text element contains the out of date text
            if textElement.text == "Max Density =":

            # If out of date text is found, replace it with the new text
                textElement.text = ("Max Density = " + str(MMaxD) + " per " + "grid cell")

        mxd2.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '2 Number of Members.mxd'))


        map_file3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'6 Templates', 'Percentage.mxd')
        mxd3 = arcpy.mapping.MapDocument(map_file3)
        df = arcpy.mapping.ListDataFrames(mxd3, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd3, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd3.save()

        # Loop through each text element in the map document
        for textElement in arcpy.mapping.ListLayoutElements(mxd3, "TEXT_ELEMENT"):

            # Check if the text element contains the out of date text
            if textElement.text == "Max%":

            # If out of date text is found, replace it with the new text
                textElement.text = ("Max % members = " + str(vmax1f) + " per " + "grid cell")

            # Check if the text element contains the out of date text
            if textElement.text == "Mean%":

            # If out of date text is found, replace it with the new text
                textElement.text = ("Mean % members = " + str(vmean1f) + " per " + "grid cell")


        mxd3.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '3 Percentage Members.mxd'))





        if Aview1 == 'true':

            # open the file with default application (ArcMap)

            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Opening data in ArcMaps")

            map1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '1 Type of membership.mxd')
            map2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '2 Number of Members.mxd')
            map3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '3 Percentage Members.mxd')

            arcpy.AddMessage("    ArcMap  " + map1)
            arcpy.AddMessage("    ArcMap  " + map2)
            arcpy.AddMessage("    ArcMap  " + map3)

            os.startfile(map1)
            os.startfile(map2)
            os.startfile(map3)

            time.sleep(15)  # sleep time in seconds...

        else:
            arcpy.AddMessage(" ")



        if PDFs == 'true':

            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Saving PDFs to " + PDFloctn)

            map_file1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '1 Type of membership.mxd')

            mxd1 = arcpy.mapping.MapDocument(map_file1)
            mxdname = mxd1.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd1.dataDrivenPages.pageCount + 1):
              mxd1.dataDrivenPages.currentPageID = pageNum
              name = str(mxd1.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd1, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
            del mxd1


            map_file2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '2 Number of Members.mxd')

            mxd2 = arcpy.mapping.MapDocument(map_file2)
            mxdname = mxd2.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd2.dataDrivenPages.pageCount + 1):
              mxd2.dataDrivenPages.currentPageID = pageNum
              name = str(mxd2.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd2, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
            del mxd2


            map_file3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'1 ArcMaps', '3 Percentage Members.mxd')
            mxd3 = arcpy.mapping.MapDocument(map_file3)
            mxdname = mxd3.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd3.dataDrivenPages.pageCount + 1):
              mxd3.dataDrivenPages.currentPageID = pageNum
              name = str(mxd3.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd3, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
            del mxd3

        else:
            arcpy.AddMessage(" ")


        arcpy.AddMessage("    Analysis completed")


        return
