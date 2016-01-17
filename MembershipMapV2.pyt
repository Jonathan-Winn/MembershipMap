# Python Toolbox used to create membership maps
# Allows user selection of input membership location data, reserves input data and ouput maps types
# Designed for use with ArcGIs 10.2.2 (Python 2.7.5)
# Created by Jonathan Winn
# See my LinkedIn page:    https://www.linkedin.com/in/jonathanwinnspatial

import arcpy
import os
import sys
from arcpy.sa import *
import time
import logging
import datetime

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
        self.description = """This tool takes input data on memberships and maps these against Post Code and population density data.
        PDF maps of membership type, density and percentage of the local population are mapped using grid cells.
        Optionally analysis examines reserve locations and calculates the local population size and number of members within user defined travel zones around reserves.
        The analysis for user provided reserves data are then compared against analysis for Local Nature Reserves (LNR) and National Nature Reserves (NNR).
        """
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        p0 = arcpy.Parameter(
            displayName="Study Area boundaries",
            name="SAboundary",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        p0.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'District_borough_unitary_region')

        p1 = arcpy.Parameter(
           displayName="Select Study Area",
            name="SAreaSQL",
            datatype="GPSQLExpression",
            parameterType="Required",
            direction="Input")
        p1.value = "NAME = 'County Durham'"
        p1.parameterDependencies = [p0.name]

        p2 = arcpy.Parameter(
            displayName="Set buffer distance around Study Area (meters)",
            name="Buffer",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        p2.value = 10000

        p3 = arcpy.Parameter(
            displayName="Set grid cell size (meters)",
            name="Grid",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        p3.value = 2000

        p4 = arcpy.Parameter(
            displayName="Scratch",
            name="Scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p4.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'03OutputData\Scratch.gdb')

        p5 = arcpy.Parameter(
            displayName="CodePoint Postcodes",
            name="CodePoint",
            datatype="DETable",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p5.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'CodePointTable')

        p6 = arcpy.Parameter(
           displayName="Set field in CodePoint with Postcodes",
            name="ValuesF",
            datatype="Field",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p6.value = 'Poscode'
        p6.parameterDependencies = [p5.name]

        p7 = arcpy.Parameter(
           displayName="Data table with memberships",
            name="MembersT",
            datatype="DETable",
            parameterType="Required",
            direction="Input")
        p7.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData', 'Memberships.csv')

        p8 = arcpy.Parameter(
           displayName="Set field in memberships table with Postcodes",
            name="PostF",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        p8.value = 'Postcode'
        p8.parameterDependencies = [p7.name]

        p9 = arcpy.Parameter(
            displayName="Outputs",
            name="Outputs",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p9.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'03OutputData\Outputs.gdb')

        p10 = arcpy.Parameter(
            displayName="Use alternative Study Area boundary? (instead of boundary file shown above)",
            name="UserStudy",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p10.value = 'false'

        p11 = arcpy.Parameter(
            displayName="Select alternative Study Area from file",
            name="AltArea",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        p11.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'Study1')

        p12 = arcpy.Parameter(
            displayName="Indicators",
            name="Indicators",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p12.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'03OutputData\Indicators.gdb')

        p13 = arcpy.Parameter(
            displayName="Include Reserve location points?",
            name="Reserves",
            datatype="GPBoolean",
            parameterType="Optional",
            category = "Optional Reserve location data use",
            direction="Input")
        p13.value = 'true'

        p14 = arcpy.Parameter(
           displayName="Reserve points data",
            name="ReservesT",
            datatype="DETable",
            parameterType="Optional",
            category = "Optional Reserve location data use",
            direction="Input")
        p14.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData', 'Reserves.csv')

        p15 = arcpy.Parameter(
            displayName="Census areas",
            name="Census",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p15.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'OA_2011_GB')

        p16 = arcpy.Parameter(
            displayName="Create PDFs?",
            name="PDFs",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p16.value = 'true'

        p17 = arcpy.Parameter(
            displayName="Open and view data in ArcMap when analysis is complete?",
            name="Aview1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p17.value = 'false'


        p18 = arcpy.Parameter(
            displayName="Set local scale buffers zone distance (meters)",
            name="Buffer1",
            datatype="GPLong",
            parameterType="Required",
            category = "Optional Reserve location data use",
            direction="Input")
        p18.value = 500

        p19 = arcpy.Parameter(
            displayName="Set landscape scale buffers zone distance (meters)",
            name="Buffer2",
            datatype="GPLong",
            parameterType="Required",
            category = "Optional Reserve location data use",
            direction="Input")
        p19.value = 2000

        p20 = arcpy.Parameter(
            displayName="Set county scale buffers zone distance (meters)",
            name="Buffer3",
            datatype="GPLong",
            parameterType="Required",
            category = "Optional Reserve location data use",
            direction="Input")
        p20.value = 8000

        return [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9, p10, p11, p12, p13,p14,p15,p16,p17,p18,p19,p20]


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
        Buffer               = parameters[2].valueAsText

        Grids                = parameters[3].valueAsText
        Scratch              = parameters[4].valueAsText
        CodePoint            = parameters[5].valueAsText

        PostcodeM            = parameters[6].valueAsText
        MembersT             = parameters[7].valueAsText
        PostF                = parameters[8].valueAsText

        Outputs              = parameters[9].valueAsText
        UserStudy            = parameters[10].valueAsText
        AltArea              = parameters[11].valueAsText

        Indicators           = parameters[12].valueAsText
        Reserves             = parameters[13].valueAsText
        ReservesT            = parameters[14].valueAsText

        Census               = parameters[15].valueAsText
        PDFs                 = parameters[16].valueAsText
        Aview1               = parameters[17].valueAsText

        Buffer1               = parameters[18].valueAsText
        Buffer2               = parameters[19].valueAsText
        Buffer3               = parameters[20].valueAsText

        B1                    = parameters[18].value
        B2                    = parameters[19].value
        B3                    = parameters[20].value



      # local parameter list

        SA_lyr               = "SA_lyr"
        Code_lyr             = "Code_lyr"
        Members_lyr          = "Members_lyr"
        PCodeOut             = os.path.join(Outputs,"AllPCodes")
        Popn100m             = os.path.join(Outputs,"Popn100m")
        Mbrs100m             = os.path.join(Outputs,"Mbrs100m")
        MembersOut           = os.path.join(Outputs,"Members")
        MembershipsOut       = os.path.join(Outputs,"Memberships")
        GridMships           = os.path.join(Outputs,"Number_Memberships")
        GridMembers          = os.path.join(Outputs,"Number_Members")
        FNScrSDOut           = os.path.join(Indicators, "Mship_Zscr_SD_IndC")
        MScrSDOut            = os.path.join(Indicators, "Mbrs_Zscr_SD_IndC")
        PcntScrSDOut         = os.path.join(Indicators, "Pcnt_Zscr_SD_IndC")
        Census_lyr           = "Census_lyr"
        PopnOut              = os.path.join(Outputs,"Population")
        DTM1                 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'DTM1000')
        PDFloctn             = os.path.join(os.path.dirname(os.path.dirname(__file__)),'04PDFs')
        Buffers_lyr          = "Buffers_lyr"
        outpath              = os.path.join(os.path.dirname(os.path.dirname(__file__)),'03OutputData')
        lnr                  = os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'LNR_GB')
        nnr                  = os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb', 'NNR_GB')
        InputsGDB            = os.path.join(os.path.dirname(os.path.dirname(__file__)),'02InputData\Inputs.gdb')
        Rlo_lyr              = os.path.join(os.path.dirname(os.path.dirname(__file__)),'10LayerFiles', 'M0loc.lyr')
        Rla_lyr              = os.path.join(os.path.dirname(os.path.dirname(__file__)),'10LayerFiles', 'M0land.lyr')
        Mloc_lyr             = os.path.join(os.path.dirname(os.path.dirname(__file__)),'10LayerFiles', 'Mloc.lyr')
        Mland_lyr            = os.path.join(os.path.dirname(os.path.dirname(__file__)),'10LayerFiles', 'Mland.lyr')

        # set full text message tracking (true for testing, false for use by user)

        fulltext             = "false"

        # set overwrite and scratch workspace

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = Scratch
        arcpy.Resample_management(DTM1, "snap", Grids)
        arcpy.env.snapRaster = "snap"
        arcpy.CheckOutExtension("Spatial")
        spatial_ref = arcpy.Describe(Census).spatialReference
        arcpy.env.outputCoordinateSystem = spatial_ref
        start_time_t0 = time.time()
        d = datetime.datetime.now()


        # set up logging

        dtstamp4 = datetime.datetime.now().strftime('MessageLog_%d_%m_%Y__hr%H.log')
        msglog2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'zlog', str(dtstamp4))
        # remove datefmt to include miliseconds
        logformat = '%(lineno)s      %(asctime)s     %(levelname)s  : %(message)s'
        datetxt =' %a  %Y-%m-%d   %H:%M:%S'
        logging.basicConfig(filename=msglog2,filemode="w", level=logging.DEBUG, format = logformat, datefmt = datetxt)
        logID = 1

        # begin messages for user

        arcpy.AddMessage(" ")
        messages.addMessage("    Tool will take between 30 mins - 1hr to complete")
        messages.addMessage("    Preparing data for analysis")

        # begin log

        logging.info("Log: " + str(d))
        logging.info("Start analysis: " + str(start_time_t0))

        arcpy.env.workspace = InputsGDB

        flist = arcpy.ListFiles("*.cdf")
        flen = len(flist)
        if flen > 0:
            messages.addMessage("    Uncompressing Input data geodatabase (first time toolbox is run: this step can be slow)")
            logging.info("Inputs were compressed, then uncompressed")
            arcpy.UncompressFileGeodatabaseData_management(InputsGDB)
        else:
            messages.addMessage("    Using uncompressed Input data geodatabase")
            logging.info("Inputs were already uncompressed")

        arcpy.env.workspace = Scratch

        # delete key datasets from any previous analysis runs

        delList = ["*NR*", "*Top*"]
        for dl in delList:
                allDX = arcpy.ListRasters(dl)
                if allDX:
                  logging.info("Rasters deleted:  ")
                  for rasterDX in allDX:
                         try:
                          arcpy.Delete_management(rasterDX)
                          logging.info("Rasters deleted:  " + str(rasterDX) )
                         except:
                          messages.addMessage("Can't delete " + str(rasterDX))

                allDX3 = arcpy.ListTables(dl)
                if allDX3:
                   logging.info("Tables deleted:  " )
                   for TableDX in allDX3:
                         try:
                          arcpy.Delete_management(TableDX)
                          logging.info("Tables deleted:  " + str(TableDX))
                         except:
                          messages.addMessage("Can't delete " + str(TableDX))

                allDX4 = arcpy.ListFeatureClasses(dl)
                if allDX3:
                  logging.info("Feature class deleted:  " )
                  for FeatDX in allDX4:
                         try:
                          arcpy.Delete_management(FeatDX)
                          logging.info("Feature classes deleted:  " + str(TableDX))
                         except:
                          messages.addMessage("Can't delete " + str(FeatDX))

        Tresult = arcpy.GetCount_management(MembersT)
        Tcount = int(Tresult.getOutput(0))
        TcountF = float(Tresult.getOutput(0))

        messages.addMessage("    Memberships input data has  " + str(Tcount) + "  records")

        arcpy.MakeFeatureLayer_management(SAboundary, SA_lyr, SAreaSQL)
        arcpy.CopyFeatures_management(SA_lyr, "StudyArea_MX")

        if UserStudy == 'true':

          arcpy.CopyFeatures_management(AltArea, "StudyArea_MX")
          logging.info("Analysis run with user supplied Study Area file")

        else:
          logging.info("Analysis run with GUI selected Study Area" )

        messages.addMessage("    Applying " + str(Buffer) + " m buffer to Study Area")

        BfrInput = "StudyArea_MX"
        BfrOut = "SA_buffer_MX"
        distance = Buffer
        sideType = "FULL"
        endType = "ROUND"
        dissolveType = "NONE"
        dissolveField = ""
        arcpy.Buffer_analysis(BfrInput, BfrOut, distance, sideType, endType, dissolveType, dissolveField)

        arcpy.CopyRows_management(MembersT, "MembersImport_MX")
        arcpy.AddIndex_management("MembersImport_MX", PostF, "PIndex", "UNIQUE", "ASCENDING")

        logging.info("Buffer created (SA_buffer_MX)")

        BfrInput = "SA_buffer_MX"
        BfrOut = "SA5k_MX"
        distance = 5000
        sideType = "FULL"
        endType = "ROUND"
        dissolveType = "NONE"
        dissolveField = ""
        arcpy.Buffer_analysis(BfrInput, BfrOut, distance, sideType, endType, dissolveType, dissolveField)

        logging.info("Full extent buffer created")

        indexes = arcpy.ListIndexes(CodePoint)
        ind_exist =  []
        for index in indexes:
                if (index.name == "PCInd2"):
                    ind_exist.append(index.name)

        if "PCInd2" in ind_exist:
            logging.info("CodePoint index exists  " + str(ind_exist))
        else:
            messages.addMessage("    Adding index to CodePoint: this step can be slow")
            arcpy.AddIndex_management(CodePoint, PostcodeM, "PCInd2", "UNIQUE", "ASCENDING")

        logging.info("Copy data (Members, CopdePoint) to in_memory" )

        in_Table = CodePoint
        x_coords = "easting"
        y_coords = "northing"
        z_coords = ""
        out_Layer = "PCodes_view"

        # Set the spatial reference
        spRef = spatial_ref

        # Make the XY event layer...
        arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, spRef, z_coords)
        arcpy.CopyFeatures_management(out_Layer,  "in_memory\AllCodes_MX")
        arcpy.MakeFeatureLayer_management(out_Layer, Code_lyr)

        arcpy.CopyRows_management("MembersImport_MX", "in_memory\MembersCopy_MX")
        arcpy.CopyRows_management(CodePoint, "in_memory\TableAllCodes")

        intabepr = "in_memory\TableAllCodes"
        fieldName1 = PostcodeM
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""
        expression1 = """!%s!.replace(" ", "")""" % (PostcodeM)

        logging.info("Update CodePoint (postcode field)")

#        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        arcpy.CalculateField_management(intabepr, fieldName1, expression1 , "PYTHON_9.3")

        intabepr = "in_memory\MembersCopy_MX"
        fieldName1 = PostF
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""
        expression1 = """!%s!.replace(" ", "")""" %(PostF)
        expression2 = "!%s!.upper()" %(PostF)

        logging.info("Update Members data (postcode field)")

#        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        arcpy.CalculateField_management(intabepr, fieldName1, expression1 , "PYTHON_9.3")
        arcpy.CalculateField_management(intabepr, fieldName1, expression2 , "PYTHON_9.3")

        messages.addMessage("    Joining location grid ref to membership postcodes")
        logging.info("Joining location grid ref to membership postcodes")

        start_time_t1 = time.time()

        inFeatures = "in_memory\MembersCopy_MX"
        joinFieldIn = PostF
        joinFieldJT = PostcodeM
        joinTable = "in_memory\TableAllCodes"
        fieldList = ["easting", "northing"]

        arcpy.JoinField_management (inFeatures, joinFieldIn, joinTable, joinFieldJT, fieldList)

        elapsed_time_seconds_tool1 = time.time() - start_time_t1

        mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
        ht1, mt1 = divmod(mt1, 60)
        timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)

        messages.addMessage("    Join succeeded at: " + str(timetaken))
        logging.info("Join succeeded at: " + str(timetaken))

        arcpy.MakeTableView_management(inFeatures, "m_view")

        logging.info("Save data membership points")

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
        arcpy.CopyFeatures_management(out_Layer, "AllMembersPoints")

        logging.info("Select unmatched membership records and export to xls" )

        arcpy.SelectLayerByAttribute_management (out_Layer, "SWITCH_SELECTION")
        arcpy.CopyFeatures_management(out_Layer, "MembershipsNotMatched")
        arcpy.MakeTableView_management(out_Layer, "NotMatch_tview")
        in_table = "NotMatch_tview"
        out_xls = os.path.join(outpath,"MembershipsNotMatched.xls")
        arcpy.TableToExcel_conversion(in_table, out_xls)

        logging.info("Copy membership point to scratch and copy to in_memory" )

        arcpy.SelectLayerByLocation_management (out_Layer, "INTERSECT", "SA_buffer_MX")
        arcpy.CopyFeatures_management(out_Layer, "MembersPoints")

        arcpy.SelectLayerByLocation_management (Code_lyr, "INTERSECT", "SA_buffer_MX")
        arcpy.CopyFeatures_management(Code_lyr, "in_memory\LocCodes_MX")

        TM = arcpy.GetCount_management("in_memory\LocCodes_MX")
        Tc = int(TM.getOutput(0))

        del Code_lyr
        del out_Layer

        arcpy.Delete_management("in_memory\AllCodes_MX")
        arcpy.Delete_management ("in_memory\MembersCopy_MX")
        arcpy.Delete_management ("in_memory\TableAllcodes")

        logging.info("Selecting Post Codes within Study Area Buffer")

        messages.addMessage("    There are   " + str(Tc) + "  Post Codes in the Study Area Buffer")


        TP = arcpy.GetCount_management("AllMembersPoints")
        TPt = int(TP.getOutput(0))
        TPff = float(TP.getOutput(0))

        Tnot = arcpy.GetCount_management("MembershipsNotMatched")
        TnotInt = int(Tnot.getOutput(0))
        Tnotf = float(Tnot.getOutput(0))

        TM = arcpy.GetCount_management("MembersPoints")
        TMi = int(TM.getOutput(0))
        TMf = float(TM.getOutput(0))

        pcntmatch2 = ((TPff / TcountF ) *100)
        pc02 = str(pcntmatch2)[0:4]
        pcntmatch3 = ((TMf / TcountF ) *100)
        pc03 = str(pcntmatch3)[0:4]
        pcntmatch4 = ((Tnotf / TcountF ) *100)
        pc04 = str(pcntmatch4)[0:4]

        messages.addMessage("    " + str(pc02) + "  % of the " + str(Tcount) + " input membership records (" + str(TPt) + " records) have valid PostCodes")
        messages.addMessage("    " + str(pc03) + "  % of the " + str(Tcount) + " input membership records (" + str(TMi) + " records) have valid PostCodes and occur within the Study Area Buffer and will be used for this analysis")

        if TnotInt > 0:
          messages.addMessage("    " + str(pc04) + "  % of the " + str(Tcount) + "   records (" + str(TnotInt) + " records) do not have valid PostCodes. Records have been exported in Excel format for checking")
          messages.addMessage("    Unmatched membership records exported to " + str(out_xls))

        logging.info("Selecting Census Areas (OA, DZ) within Study Area Buffer")

        arcpy.MakeFeatureLayer_management(Census, Census_lyr)
        arcpy.SelectLayerByLocation_management (Census_lyr, "INTERSECT", "SA_buffer_MX")
        arcpy.CopyFeatures_management(Census_lyr, "in_memory\LocCensus_MX")

        Tcc = arcpy.GetCount_management("in_memory\LocCensus_MX")
        Tcct = int(Tcc.getOutput(0))

        messages.addMessage("    There are  " + str(Tcct) + "  Census Areas (OA, DZ) intersecting the Study Area Buffer")

        arcpy.CopyFeatures_management("MembersPoints", "in_memory\Loc_MX")

        logging.info("Joining Census Areas (OA, DZ) data to local Post Codes points" )

        target_features = "in_memory\Loc_MX"
        join_features = "in_memory\LocCensus_MX"
        out_feature_class = "LocDataP_MX"
        arcpy.SpatialJoin_analysis(target_features, join_features, out_feature_class)

        TD = arcpy.GetCount_management("LocDataP_MX")
        TDct = int(TD.getOutput(0))

        messages.addMessage("    There are  " + str(TDct) + "  matching memberships with joined Cenus Areas (OA, DZ) data")

        del Census_lyr
        arcpy.Delete_management("in_memory\Loc_MX")

        # calculate how many postcodes points per Census Area

        logging.info(" Calculate number of Post Code points (Nm1) per Census Area (OAC) (members points only)")

        inTable = "LocDataP_MX"
        outStatsTable = "stats_out_MX"
        statsFields = [["Nm1", "SUM"]]
        caseField = "OAC"

        arcpy.Statistics_analysis(inTable, outStatsTable, statsFields, caseField)

        # Join the data field back to the point data

        logging.info("Join field  - sum of postcodes  (members points only)")

        arcpy.CopyFeatures_management("LocDataP_MX", "in_memory\LocD")
        inFeatures = "in_memory\LocD"
        joinField = "OAC"
        joinTable = "stats_out_MX"
        fieldList = ["SUM_Nm1"]
        arcpy.JoinField_management (inFeatures, joinField, joinTable, joinField, fieldList)

        messages.addMessage("    Calculate  local population sizes")

        logging.info("Calculate estimated average population per Post Code point (cenus popn / no. of post code points)  (members points only)")




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

        arcpy.Delete_management("in_memory\LocD")

        # calc to find total local population size grid

        logging.info("Spatial join of census polygon data to membership points")

        target_features = "in_memory\LocCodes_MX"
        join_features = "in_memory\LocCensus_MX"
        out_feature_class = "LocCodePoints_plus_MX"
        arcpy.SpatialJoin_analysis(target_features, join_features, out_feature_class)

        # calculate how many postcodes points per Census Area

        logging.info("Calculate number of Post Code points (Nm1) per Census Area (OAC) (all points)")

        inTable = "LocCodePoints_plus_MX"
        outStatsTable = "stats_out_MX"
        statsFields = [["Nm1", "SUM"]]
        caseField = "OAC"
        arcpy.Statistics_analysis(inTable, outStatsTable, statsFields, caseField)

        # Join the data field back to the point data

        logging.info("Join field  - sum of postcodes  (all points)")

        arcpy.CopyFeatures_management("LocCodePoints_plus_MX", "in_memory\CodePAll")
        inFeatures = "in_memory\CodePAll"
        joinField = "OAC"
        joinTable = "stats_out_MX"
        fieldList = ["SUM_Nm1"]
        arcpy.JoinField_management (inFeatures, joinField, joinTable, joinField, fieldList)

        # add and calculate popn fields

        logging.info("Calculate estimated average population per Post Code point (cenus popn / no. of post code points)  (all points)")

        intabepr = "in_memory\CodePAll"
        fieldName1 = "PopnX"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""
        expression1 = "!all_people_x!  / !SUM_Nm1! "
        arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.CalculateField_management(intabepr, fieldName1, expression1 , "PYTHON_9.3")

        arcpy.CopyFeatures_management("in_memory\CodePAll", PCodeOut)

        logging.info( "Creating  100  m grid map of population size")

        # set extent for rasters

        ext2                 = arcpy.Describe("SA5k_MX").extent
        arcpy.env.extent     = ext2

        inFeatures = PCodeOut
        valField = "PopnX"
        outRaster = Popn100m
        assignmentType = "SUM"
        priorityField = ""
        cellSizePop = 100
        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSizePop)

        logging.info( "Creating  100  m  grid map of members")

        inFeatures = MembersOut
        valField = "Members"
        outRaster = Mbrs100m
        assignmentType = "SUM"
        priorityField = ""
        cellSize100 = 100
        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize100)



        intabepr = MembersOut
        fieldName1 = "Memberships"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""
        arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.CalculateField_management(intabepr, fieldName1, 1 , "PYTHON_9.3")

        result = arcpy.GetCount_management(MembersOut)
        Mcount = int(result.getOutput(0))

        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of memberships")

        inFeatures = MembersOut
        valField = "Memberships"
        outRaster = GridMships
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids
        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        logging.info( "Calculate SD grids, Z scores of memberships")

        MaxD            = arcpy.GetRasterProperties_management(GridMships,property_type="MAXIMUM")

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



        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of members")

        inFeatures = MembersOut
        valField = "Members"
        outRaster = GridMembers
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids
        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        logging.info( "Calculate SD grids, Z scores of members")

        MMaxD            = arcpy.GetRasterProperties_management(GridMembers,property_type="MAXIMUM")

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


        messages.addMessage("    Creating  " + str(Grids) + "  m grid maps of percent population membership")

        inFeatures = MembersOut
        valField = "PopnX"
        outRaster = PopnOut
        assignmentType = "SUM"
        priorityField = ""
        cellSize = Grids
        arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, assignmentType, priorityField, cellSize)

        logging.info( "Calculate SD grids, Z scores of percent population membershipship")


        VarP1              = Divide(GridMembers, PopnOut)
        VarP2              = Times (VarP1, 100)
        VarP2.save(os.path.join(Outputs, "Percent"))

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

        inZoneData = "SA_buffer_MX"
        zoneField = "NAME"
        inValueRaster = Popn100m
        outTable = "TotalPopn"
        outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

        totpop = arcpy.da.SearchCursor("TotalPopn",("SUM",)).next()[0]
        totpop2 = int(totpop)
        totpop3 = '{0:,}'.format(totpop2)
        messages.addMessage("    Study Area Buffer: Total population is  " + str(totpop3) + " people  " )


        inZoneData = "SA_buffer_MX"
        zoneField = "NAME"
        inValueRaster = Mbrs100m
        outTable = "TotalMbrs"
        outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

        totmem = arcpy.da.SearchCursor("TotalMbrs",("SUM",)).next()[0]
        totmem2 = int(totmem)
        totmem3 = '{0:,}'.format(totmem2)
        messages.addMessage("    Study Area Buffer: Total number of members is  " + str(totmem3) )







        if Reserves == 'true':

            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Mapping Reserve locations")

            arcpy.CopyRows_management(ReservesT, "in_memory\ReservesCopy_MX")
            inFeatures = "in_memory\ReservesCopy_MX"
            arcpy.MakeTableView_management(inFeatures, "r_view")

            in_Table = "r_view"
            x_coords = "x"
            y_coords = "y"
            z_coords = ""
            out_Layer = "reserves_view"

            # Set the spatial reference
            spRef = spatial_ref

            # Make the XY event layer...
            arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, spRef, z_coords)
            arcpy.CopyFeatures_management(out_Layer, "AllReservesPoints")
            TR = arcpy.GetCount_management(ReservesT)
            TRt = int(TR.getOutput(0))

            messages.addMessage("    There are  " + str(TRt) + "  reserves in the reserves input data")

            arcpy.SelectLayerByLocation_management (out_Layer, "INTERSECT", "SA_buffer_MX")
            arcpy.CopyFeatures_management(out_Layer, "ReservesPoints")
            TRss = arcpy.GetCount_management(out_Layer)
            TRsst = int(TRss.getOutput(0))

            messages.addMessage("    There are  " + str(TRsst) + "  reserves in the Study Area buffer")

            arcpy.SelectLayerByAttribute_management(out_Layer, "CLEAR_SELECTION")


            arcpy.AddMessage("    Creating travel zone buffers around reserves")

            inFeatures = "ReservesPoints"
            outFeatureClass = "multibuffer1"
            distances = [Buffer1, Buffer2, Buffer3]
            bufferUnit = "meters"
            arcpy.MultipleRingBuffer_analysis(inFeatures, outFeatureClass, distances, bufferUnit, "", "ALL")

            logging.info( "Clip buffers to SA buffer, convert to raster")

            in_features = "multibuffer1"
            clip_features = "SA_buffer_MX"
            out_feature_class = "Buffers"
            xy_tolerance = ""
            arcpy.Clip_analysis(in_features, clip_features, out_feature_class, xy_tolerance)

            intabepr = "Buffers"
            fieldName1 = "Zone"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            expressionP = "!distance!"
            arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

            inFeature = "Buffers"
            outRaster = "RBuffers"
            cellSize = 100
            field = "Zone"
            arcpy.FeatureToRaster_conversion(inFeature, field, outRaster, cellSize)

            logging.info( "Zonal stats - popn per buffer, members per buffer and total popn for study area")

            inZoneData = "RBuffers"
            zoneField = "Value"
            inValueRaster = Popn100m
            outTable = "ZonePopn"
            outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

            inZoneData = "RBuffers"
            zoneField = "Value"
            inValueRaster = Mbrs100m
            outTable = "MbrsPopn"
            outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

            intabepr = "ZonePopn"
            fieldName1 = "Percent"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            expressionP = "(!SUM!/%d)*100" %(totpop)
            arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

            intabepr = "MbrsPopn"
            fieldName1 = "Percent"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            expressionP = "(!SUM!/%d)*100" %(totpop)
            arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")


            # Create LNR_GB distance zones and analysis - for use with graph insert

            arcpy.MakeFeatureLayer_management(lnr, "lnr_lyr")
            arcpy.SelectLayerByLocation_management ("lnr_lyr", "INTERSECT", "SA_buffer_MX")
            arcpy.CopyFeatures_management("lnr_lyr", "LocLNR_MX")

            TLNR = arcpy.GetCount_management("LocLNR_MX")
            TLNRt = int(TLNR.getOutput(0))

            if TLNRt > 0:

                messages.addMessage("    There are  " + str(TLNRt) + "  LNRs in the Study Area buffer")

                inFeatures = "LocLNR_MX"
                outFeatureClass = "lnrbuffer_MX"
                distances = [Buffer1, Buffer2, Buffer3]
                bufferUnit = "meters"
                arcpy.MultipleRingBuffer_analysis(inFeatures, outFeatureClass, distances, bufferUnit, "", "ALL")

                logging.info( "LNR - clip, convert to rasters")

                in_features = "lnrbuffer_MX"
                clip_features = "SA_buffer_MX"
                out_feature_class = "LNR_Buffers"
                xy_tolerance = ""
                arcpy.Clip_analysis(in_features, clip_features, out_feature_class, xy_tolerance)

                intabepr = "LNR_Buffers"
                fieldName1 = "Zone"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "!distance!"
                arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

                inFeature = "LNR_Buffers"
                outRaster = "LNR_rast"
                cellSize = 100
                field = "Zone"
                arcpy.FeatureToRaster_conversion(inFeature, field, outRaster, cellSize)

                logging.info( "LNR - Zonal stats and field calcs - popn")

                inZoneData = "LNR_rast"
                zoneField = "Value"
                inValueRaster = Popn100m
                outTable = "LNRPopn"
                outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

                intabepr = "LNRPopn"
                fieldName1 = "Percent"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "(!SUM!/%d)*100" %(totpop)
                arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

                logging.info("LNR - Zonal stats and field calcs - members")

                inZoneData = "LNR_rast"
                zoneField = "Value"
                inValueRaster = Mbrs100m
                outTable = "LNRmem"
                outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

                intabepr = "LNRmem"
                fieldName1 = "Percent"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "(!SUM!/%d)*100" %(totpop)
                arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

            if TLNRt == 0:
                arcpy.AddWarning("    There are no LNRs in the Study Area buffer")
                arcpy.AddWarning("    Ideally re-run the analysis for a larger Study Area or using a larger buffer zone")
                logging.info( "There are no LNRs in the Study Area buffer")

            # Create NNR_GB distance zones and analysis - for use with graph insert

            arcpy.MakeFeatureLayer_management(nnr, "nnr_lyr")
            arcpy.SelectLayerByLocation_management ("nnr_lyr", "INTERSECT", "SA_buffer_MX")
            arcpy.CopyFeatures_management("nnr_lyr", "LocNNR_MX")

            TNNR = arcpy.GetCount_management("LocNNR_MX")
            TNNRt = int(TNNR.getOutput(0))

            if TNNRt > 0:

                messages.addMessage("    There are  " + str(TNNRt) + "  NNRs in the Study Area buffer")

                inFeatures = "LocNNR_MX"
                outFeatureClass = "nnrbuffer_MX"
                distances = [Buffer1, Buffer2, Buffer3]
                bufferUnit = "meters"
                arcpy.MultipleRingBuffer_analysis(inFeatures, outFeatureClass, distances, bufferUnit, "", "ALL")

                logging.info( "NNR - clip, convert to rasters")

                in_features = "nnrbuffer_MX"
                clip_features = "SA_buffer_MX"
                out_feature_class = "NNR_Buffers"
                xy_tolerance = ""
                arcpy.Clip_analysis(in_features, clip_features, out_feature_class, xy_tolerance)

                intabepr = "NNR_Buffers"
                fieldName1 = "Zone"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "!distance!"
                arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

                inFeature = "NNR_Buffers"
                outRaster = "NNR_rast"
                cellSize = 100
                field = "Zone"
                arcpy.FeatureToRaster_conversion(inFeature, field, outRaster, cellSize)

                logging.info( "NNR - Zonal stats and field calcs - popn")

                inZoneData = "NNR_rast"
                zoneField = "Value"
                inValueRaster = Popn100m
                outTable = "NNRPopn"
                outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

                intabepr = "NNRPopn"
                fieldName1 = "Percent"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "(!SUM!/%d)*100" %(totpop)
                arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

                logging.info( "NNR - Zonal stats and field calcs - members")

                inZoneData = "NNR_rast"
                zoneField = "Value"
                inValueRaster = Mbrs100m
                outTable = "NNRmem"
                outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "SUM")

                intabepr = "NNRmem"
                fieldName1 = "Percent"
                fieldPrecision = ""
                fieldAlias = ""
                fieldLength = ""
                expressionP = "(!SUM!/%d)*100" %(totpop)
                arcpy.AddField_management(intabepr, fieldName1, "DOUBLE", fieldPrecision, "", "", fieldAlias, "NULLABLE")
                arcpy.CalculateField_management(intabepr, fieldName1, expressionP, "PYTHON_9.3")

            if TNNRt == 0:

                arcpy.AddWarning("    There are no NNRs in the Study Area buffer")
                arcpy.AddWarning("    Ideally re-run the analysis for a larger Study Area or using a larger buffer zone")


        if Reserves == 'true':

            # Set up reserve distance analysis

            messages.addMessage("    Using travel distance zones: " + Buffer1 + "m, " + Buffer2 + "m, " + Buffer3 + "m")
            logging.info( "Using travel distance zones: " + Buffer1 + "m, " + Buffer2 + "m, " + Buffer3 + "m")

            # Set local variables - population

            inPointFeatures = PCodeOut
            field = "PopnX"
            cellSize = 100
            neighborhood0 = NbrCircle(B3, "MAP")
            neighborhood1 = NbrCircle(B2, "MAP")
            neighborhood2 = NbrCircle(B1, "MAP")

            # Execute PointStatistics - population

            arcpy.AddMessage("    Calculating population sizes in travel distance zones")

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood0, "SUM")
            outPointStatistics.save("Popn100mCounty")

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood1, "SUM")
            outPointStatistics.save("Popn100mLandscape")

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood2, "SUM")
            outPointStatistics.save("Popn100mLocal")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            inPointFeatures = MembersOut
            field = "Members"

            # Execute PointStatistics - members

            logging.info( "Calculating number of members in travel distance zones")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood0, "SUM")
            outPointStatistics.save("Mem100mCounty")

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood1, "SUM")
            outPointStatistics.save("Mem100mLandscape")

            outPointStatistics = PointStatistics(inPointFeatures, field, cellSize,  neighborhood2, "SUM")
            outPointStatistics.save("Mem100mLocal")

            logging.info("Extracting data to ReservesPoints")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            inPointFeatures = "ReservesPoints"
            inRasterList = [["Popn100mLocal", "PopnLocal"], ["Popn100mLandscape", "PopnLandscape"] , ["Popn100mCounty", "PopnCounty"], ["Mem100mLocal", "MbsLo1"], ["Mem100mLandscape", "MbsLa2"] , ["Mem100mCounty", "MbsCo3"]]
            ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")

            # this step required due to test issue T15 (resolved: landscape size)

            intabepr = "ReservesPoints"
            fieldName1 = "MbsLocal"
            fieldName2 = "MbsLandscape"
            fieldName3 = "MbsCounty"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            expressionx1 = "!MbsLo1!"
            expressionx2 = "!MbsLa2!"
            expressionx3 = "!MbsCo3!"
            arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName1, expressionx1, "PYTHON_9.3")
            arcpy.AddField_management(intabepr, fieldName2, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName2, expressionx2, "PYTHON_9.3")
            arcpy.AddField_management(intabepr, fieldName3, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.CalculateField_management(intabepr, fieldName3, expressionx3, "PYTHON_9.3")

            inFeatures = "ReservesPoints"
            arcpy.MakeTableView_management(inFeatures, "table_view")
            in_table = "table_view"
            out_xls = os.path.join(outpath,"ReservesPopulations.xls")
            arcpy.TableToExcel_conversion(in_table, out_xls)

            arcpy.AddMessage("    Exporting reserves analysis data in Excel format to " + str(out_xls) )

            # make seperate data tables for each buffer zone and only show top ranked reserves

            logging.info("Saving data tables sorted by nearby population size")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))


            arcpy.Sort_management("ReservesPoints", "LocalReserves", [["PopnLocal", "DESCENDING"]])
            in_features = "LocalReserves"
            out_feature_class = "TopTLocalReserves"
            where_clause = "OBJECTID <= 15 AND PopnLocal >=1"
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopTLocalReserves")
            fieldNameList = []
            exclude = ["NAME", "Name", "PopnLocal"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopTLocalReserves", fieldNameList)

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))


            arcpy.Sort_management("ReservesPoints", "LandscapeReserves", [["PopnLandscape", "DESCENDING"]])
            in_features = "LandscapeReserves"
            out_feature_class = "TopTLandscapeReserves"
            where_clause = "OBJECTID <= 15 AND PopnLandscape >=1"
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopTLandscapeReserves")
            fieldNameList = []
            exclude = ["NAME", "Name",  "PopnLandscape"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopTLandscapeReserves", fieldNameList)


            arcpy.Sort_management("ReservesPoints", "CountyReserves", [["PopnCounty", "DESCENDING"]])
            in_features = "CountyReserves"
            out_feature_class = "TopTCountyReserves"
            where_clause = "OBJECTID <= 15 AND PopnCounty >=1"
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopTCountyReserves")
            fieldNameList = []
            exclude = ["NAME", "Name", "PopnCounty"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopTCountyReserves", fieldNameList)


            # repeat, based on no. of members ..........

            logging.info("Saving data tables sorted by nearby number of members")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            arcpy.Sort_management("ReservesPoints", "MLocalReserves", [["MbsLocal", "DESCENDING"]])
            in_features = "MLocalReserves"
            out_feature_class = "TopMLocalReserves"
            where_clause = "OBJECTID <= 15 AND MbsLocal>=1"
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopMLocalReserves")
            fieldNameList = []
            exclude = ["NAME", "Name", "MbsLocal"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopMLocalReserves", fieldNameList)


            arcpy.Sort_management("ReservesPoints", "MLandscapeReserves", [["MbsLandscape", "DESCENDING"]])
            in_features = "MLandscapeReserves"
            out_feature_class = "TopMLandscapeReserves"
            where_clause = "OBJECTID <= 15 AND MbsLandscape >=1 "
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopMLandscapeReserves")
            fieldNameList = []
            exclude = ["NAME", "Name",  "MbsLandscape"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopMLandscapeReserves", fieldNameList)


            arcpy.Sort_management("ReservesPoints", "MCountyReserves", [["MbsCounty", "DESCENDING"]])
            in_features = "MCountyReserves"
            out_feature_class = "TopMCountyReserves"
            where_clause = "OBJECTID <= 15 AND MbsCounty>=1"
            arcpy.TableSelect_analysis(in_features, out_feature_class, where_clause)

            fieldObjectList = arcpy.ListFields("TopMCountyReserves")
            fieldNameList = []
            exclude = ["NAME", "Name", "MbsCounty"]
            for field in fieldObjectList:
                if not field.required:
                    if not field.name in exclude:
                        fieldNameList.append(field.name)
            arcpy.DeleteField_management("TopMCountyReserves", fieldNameList)




        arcpy.AddMessage("    Updating ArcMap extents, text, and data tables")
        logging.info ("Updating ArcMap extents, text, and data tables")

        map_file1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T1Type.mxd')
        mxd1 = arcpy.mapping.MapDocument(map_file1)
        df = arcpy.mapping.ListDataFrames(mxd1, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd1, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd1.save()

        for textElement in arcpy.mapping.ListLayoutElements(mxd1, "TEXT_ELEMENT"):
            if textElement.text == "Text1":
                textElement.text = ("Memberships = " + str(Mcount) + " records" )
            if textElement.text == "Text0":
                textElement.text = (str(Tcount) + " records" )
        mxd1.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '1TypeofMembership.mxd'))

        logging.info ("ArcMap 01 updated")

        map_file2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T2MembershipDensity.mxd')
        mxd2 = arcpy.mapping.MapDocument(map_file2)
        df = arcpy.mapping.ListDataFrames(mxd2, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd2, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd2.save()

        for textElement in arcpy.mapping.ListLayoutElements(mxd2, "TEXT_ELEMENT"):
            if textElement.text == "Max Density =":
                textElement.text = ("Max Density = " + str(MaxD) + " per " + "grid cell")
            if textElement.text == "Grid%":
                textElement.text = ("Grid cells = " + str(Grids) + " m ")
            if textElement.text == "M1%":
                textElement.text = ( str(TMi) )
        mxd2.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '2DensityofMemberships.mxd'))

        logging.info ("ArcMap 02 updated")

        map_file3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T3MemberDensity.mxd')
        mxd3 = arcpy.mapping.MapDocument(map_file3)
        df = arcpy.mapping.ListDataFrames(mxd3, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd3, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd3.save()

        for textElement in arcpy.mapping.ListLayoutElements(mxd3, "TEXT_ELEMENT"):
            if textElement.text == "Max Density =":
                textElement.text = ("Max Density = " + str(MMaxD) + " per " + "grid cell")
            if textElement.text == "Grid%":
                textElement.text = ("Grid cells = " + str(Grids) + " m ")
            if textElement.text == "M1%":
                textElement.text = ( str(totmem3) )
        mxd3.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '3DensityofMembers.mxd'))

        logging.info ("ArcMap 03 updated")

        map_file4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T4Percentage.mxd')
        mxd4 = arcpy.mapping.MapDocument(map_file4)
        df = arcpy.mapping.ListDataFrames(mxd4, "Memberships")[0]
        slyr = arcpy.mapping.ListLayers(mxd4, "SA_buffer", df)[0]
        slyrextent = slyr.getExtent()
        df.extent = slyrextent
        mxd4.save()

        for textElement in arcpy.mapping.ListLayoutElements(mxd4, "TEXT_ELEMENT"):
            if textElement.text == "Max%":
                maxt =str(vmax1f)
                maxtv = maxt[0:4]
                textElement.text = ("Max % members = " + str(maxtv) + " " )
            if textElement.text == "Mean%":
                vp =str(vmean1f)
                vp3 = vp[0:4]
                textElement.text = ("Mean % members = " + vp3 + " ")
            if textElement.text == "Grid%":
                textElement.text = ("Grid cells = " + str(Grids) + " m ")
        mxd4.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '4PercentageMembers.mxd'))

        logging.info ("ArcMap 04 updated")








        if Reserves == 'true':

            map_file5 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T5ReservesPopn2Scale.mxd')
            mxd5 = arcpy.mapping.MapDocument(map_file5)
            df = arcpy.mapping.ListDataFrames(mxd5, "Memberships")[0]
            slyr = arcpy.mapping.ListLayers(mxd5, "SA_buffer", df)[0]
            slyrextent = slyr.getExtent()
            df.extent = slyrextent
            mxd5.save()

            df2 = arcpy.mapping.ListDataFrames(mxd5, "M2")[0]
            slyr = arcpy.mapping.ListLayers(mxd5, "SA_buffer", df2)[0]
            slyrextent = slyr.getExtent()
            df2.extent = slyrextent
            mxd5.save()

            for textElement in arcpy.mapping.ListLayoutElements(mxd5, "TEXT_ELEMENT"):
                if textElement.text == "Tx1%":
                    textElement.text = (  "Local (up to " + Buffer1 + " m)" + "  Landscape (" + Buffer1 + " to " + Buffer2 + " m)")
                if textElement.text == "Tx2%":
                    textElement.text = (  "County (" + Buffer2 + " to " + Buffer3 + " m)" )
                if textElement.text == "Grid%":
                    textElement.text = ("Grid cells = " + str(Grids) + " m ")
                if textElement.text == "T1%":
                    textElement.text = ("Total population in the Study Area Buffer = " + str(totpop3) )

            tab1 = arcpy.mapping.ListTableViews(mxd5, "ZonePopn", df)[0]
            rep1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports', 'PZone2.rlf')
            img1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'nw1.tiff')
            arcpy.mapping.ExportReport(tab1, rep1, img1)
            for image in arcpy.mapping.ListLayoutElements(mxd5, "PICTURE_ELEMENT"):
                if image.name == "tt":
                    image.sourceImage = img1

            Tplo = arcpy.GetCount_management("TopTLocalReserves")
            Tplot = int(Tplo.getOutput(0))

            if Tplot > 0:
                tab2 = arcpy.mapping.ListTableViews(mxd5, "TopTLocalReserves", df)[0]
                rep2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports', 'Local.rlf')
                img2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'nw2.tiff')
                arcpy.mapping.ExportReport(tab2, rep2, img2)
                for image in arcpy.mapping.ListLayoutElements(mxd5, "PICTURE_ELEMENT"):
                    if image.name == "loc":
                        image.sourceImage = img2

            else:
                img2x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'plo0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "loc":
                        image.sourceImage = img2x

            Tpla = arcpy.GetCount_management("TopTLandscapeReserves")
            Tplat = int(Tpla.getOutput(0))

            if Tplat > 0:
                tab3 = arcpy.mapping.ListTableViews(mxd5, "TopTLandscapeReserves", df)[0]
                rep3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports','Land.rlf')
                img3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'nw3.tiff')
                arcpy.mapping.ExportReport(tab3, rep3, img3)
                for image in arcpy.mapping.ListLayoutElements(mxd5, "PICTURE_ELEMENT"):
                    if image.name == "land":
                        image.sourceImage = img3

            else:
                img3x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'pla0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "land":
                        image.sourceImage = img3x

            Tcr = arcpy.GetCount_management("TopTCountyReserves")
            Tcrt = int(Tcr.getOutput(0))

            if Tcrt > 0:
                tab4 = arcpy.mapping.ListTableViews(mxd5, "TopTCountyReserves", df)[0]
                rep4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports','County.rlf')
                img4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'nw4.tiff')
                arcpy.mapping.ExportReport(tab4, rep4, img4)
                for image in arcpy.mapping.ListLayoutElements(mxd5, "PICTURE_ELEMENT"):
                    if image.name == "county":
                        image.sourceImage = img4

            else:
                img4x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'pc0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "county":
                        image.sourceImage = img4x

            intabepr = "ReservesPoints"
            fieldName1 = "PLoClass"
            fieldName2 = "PLaClass"
            fieldName3 = "PCoClass"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.AddField_management(intabepr, fieldName2, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.AddField_management(intabepr, fieldName3, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")


            outStatsTable = "stats_plocal_out_MX"
            statsFields = [["PopnLocal", "MIN"],["PopnLocal", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_plocal_out_MX",("MIN_PopnLocal",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("PopnLocal: Min =  " + str(mlanmin2) )
                logging.info("PopnLocal: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_plocal_out_MX",("MAX_PopnLocal",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("PopnLocal: Max =  " + str(mlanmax2) )
                logging.info("PopnLocal: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 4
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("PopnLocal: interval =  " + str(eqint2) )
                logging.info("PopnLocal: range =  " + str(mrange) )

                pcls1 = mlanmin2 + eqint2
                pcls2 = mlanmin2 + eqint2 + eqint2
                pcls3 = mlanmin2 + eqint2 + eqint2 + eqint2

                updateFields = ("PopnLocal", "PLoClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= pcls1):
                            row[1] = 1
                        elif (row[0] > pcls1 and row[0] <= pcls2 ) :
                            row[1] = 2
                        elif (row[0] > pcls2 and row[0] <= pcls3 ) :
                            row[1] = 3
                        elif (row[0] > pcls3) :
                            row[1] = 4
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("PopnLocal: no population present in 'local' travel distance" )


            outStatsTable = "stats_pout_MX"
            statsFields = [["PopnLandscape", "MIN"],["PopnLandscape", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_pout_MX",("MIN_PopnLandscape",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("PopnLandscape: Min =  " + str(mlanmin2) )
                logging.info("PopnLandscape: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_pout_MX",("MAX_PopnLandscape",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("PopnLandscape: Max =  " + str(mlanmax2) )
                logging.info("PopnLandscape: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 3
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("PopnLandscape: interval =  " + str(eqint2) )
                logging.info("PopnLandscape: range =  " + str(mrange) )

                pcls1 = mlanmin2 + eqint2
                pcls2 = mlanmin2 + eqint2 + eqint2
                pcls3 = mlanmin2 + eqint2 + eqint2 + eqint2

                updateFields = ("PopnLandscape", "PLaClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= pcls1):
                            row[1] = 1
                        elif (row[0] > pcls1 and row[0] <= pcls2 ) :
                            row[1] = 2
                        elif (row[0] > pcls2 and row[0] <= pcls3 ) :
                            row[1] = 3
                        elif (row[0] > pcls3) :
                            row[1] = 4
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("PopnLandscape: no population present in 'landscape' travel distance" )

            outStatsTable = "stats_pcounty_out_MX"
            statsFields = [["PopnCounty", "MIN"],["PopnCounty", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_pcounty_out_MX",("MIN_PopnCounty",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("PopnCounty: Min =  " + str(mlanmin2) )
                logging.info("PopnCounty: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_pcounty_out_MX",("MAX_PopnCounty",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("PopnCounty: Max =  " + str(mlanmax2) )
                logging.info("PopnCounty: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 3
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("PopnCounty: interval =  " + str(eqint2) )
                logging.info("PopnCounty: range =  " + str(mrange) )

                pcls1 = mlanmin2 + eqint2
                pcls2 = mlanmin2 + eqint2 + eqint2
                pcls3 = mlanmin2 + eqint2 + eqint2 + eqint2

                updateFields = ("PopnCounty", "PCoClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= pcls1):
                            row[1] = 1
                        elif (row[0] > pcls1 and row[0] <= pcls2 ) :
                            row[1] = 2
                        elif (row[0] > pcls2 and row[0] <= pcls3 ) :
                            row[1] = 3
                        elif (row[0] > pcls3) :
                            row[1] = 4
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("PopnCounty: no population present in 'county' travel distance" )

            mxd5.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '5ReservesPopulation.mxd'))

            logging.info ("ArcMap 05 updated")





            map_file6 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'06Templates', 'T6ReservesMember2Scale.mxd')
            mxd6 = arcpy.mapping.MapDocument(map_file6)
            df = arcpy.mapping.ListDataFrames(mxd6, "Memberships")[0]
            slyr = arcpy.mapping.ListLayers(mxd6, "SA_buffer", df)[0]
            slyrextent = slyr.getExtent()
            df.extent = slyrextent
            mxd6.save()

            df2 = arcpy.mapping.ListDataFrames(mxd6, "M2")[0]
            slyr = arcpy.mapping.ListLayers(mxd6, "SA_buffer", df2)[0]
            slyrextent = slyr.getExtent()
            df2.extent = slyrextent
            mxd6.save()

            for textElement in arcpy.mapping.ListLayoutElements(mxd6, "TEXT_ELEMENT"):
                if textElement.text == "Tx1%":
                    textElement.text = (  "Local (up to " + Buffer1 + " m)" + "  Landscape (" + Buffer1 + " to " + Buffer2 + " m)")
                if textElement.text == "Tx2%":
                    textElement.text = (  "County (" + Buffer2 + " to " + Buffer3 + " m)" )
                if textElement.text == "Grid%":
                    textElement.text = ("Grid cells = " + str(Grids) + " m ")
                if textElement.text == "T1%":
                    textElement.text = ("Total number of members in the Study Area Buffer = " + str(totmem3) )

            tab1 = arcpy.mapping.ListTableViews(mxd6, "MbrsPopn", df)[0]
            rep1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports', 'MbrZone.rlf')
            img1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'M1.tiff')
            arcpy.mapping.ExportReport(tab1, rep1, img1)
            for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                if image.name == "tt":
                    image.sourceImage = img1

            Tmlo = arcpy.GetCount_management("TopMLocalReserves")
            Tmlot = int(Tmlo.getOutput(0))

            if Tmlot > 0:
                tab2 = arcpy.mapping.ListTableViews(mxd6, "TopMLocalReserves", df)[0]
                rep2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports', 'MLocal.rlf')
                img2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'M2.tiff')
                arcpy.mapping.ExportReport(tab2, rep2, img2)
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "loc":
                        image.sourceImage = img2

            else:
                img2x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'mlo0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "loc":
                        image.sourceImage = img2x

            Tmla = arcpy.GetCount_management("TopMLandscapeReserves")
            Tmlat = int(Tmla.getOutput(0))

            if Tmlat > 0:
                tab3 = arcpy.mapping.ListTableViews(mxd6, "TopMLandscapeReserves", df)[0]
                rep3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports','MLand.rlf')
                img3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'M3.tiff')
                arcpy.mapping.ExportReport(tab3, rep3, img3)
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "land":
                        image.sourceImage = img3

            else:
                img3x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'mla0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "land":
                        image.sourceImage = img3x

            Tmc = arcpy.GetCount_management("TopMCountyReserves")
            Tmct = int(Tmc.getOutput(0))

            if Tmct > 0:
                tab4 = arcpy.mapping.ListTableViews(mxd6, "TopMCountyReserves", df)[0]
                rep4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'08Reports','MCounty.rlf')
                img4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'M4.tiff')
                arcpy.mapping.ExportReport(tab4, rep4, img4)
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "county":
                        image.sourceImage = img4

            else:
                img4x = os.path.join(os.path.dirname(os.path.dirname(__file__)),'09Images', 'mc0.tif')
                for image in arcpy.mapping.ListLayoutElements(mxd6, "PICTURE_ELEMENT"):
                    if image.name == "county":
                        image.sourceImage = img4x

            intabepr = "ReservesPoints"
            fieldName1 = "MbsLoClass"
            fieldName2 = "MbsLaClass"
            fieldName3 = "MbsCoClass"
            fieldPrecision = ""
            fieldAlias = ""
            fieldLength = ""
            arcpy.AddField_management(intabepr, fieldName1, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.AddField_management(intabepr, fieldName2, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")
            arcpy.AddField_management(intabepr, fieldName3, "LONG", fieldPrecision, "", "", fieldAlias, "NULLABLE")


            outStatsTable = "stats_local_out_MX"
            statsFields = [["MbsLocal", "MIN"],["MbsLocal", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_local_out_MX",("MIN_MbsLocal",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("MbsLocal: Min =  " + str(mlanmin2) )
                logging.info("MbsLocal: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_local_out_MX",("MAX_MbsLocal",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("MbsLocal: Max =  " + str(mlanmax2) )
                logging.info("MbsLocal: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 3
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("MbsLocal: interval =  " + str(eqint2) )
                logging.info("MbsLocal: range =  " + str(mrange) )

                cls1 = mlanmin2 + eqint2
                cls3 = mlanmin2 + eqint2 + eqint2

                updateFields = ("MbsLocal", "MbsLoClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= cls1):
                            row[1] = 1
                        elif (row[0] >= cls3) :
                            row[1] = 3
                        elif (row[0] > cls1 and row[0]  < cls3) :
                            row[1] = 2
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("MbsLocal: no members present in 'local' travel distance" )

            outStatsTable = "stats_out_MX"
            statsFields = [["MbsLandscape", "MIN"],["MbsLandscape", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_out_MX",("MIN_MbsLandscape",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("MbsLandscape: Min =  " + str(mlanmin2) )
                logging.info("MbsLandscape: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_out_MX",("MAX_MbsLandscape",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("MbsLandscape: Max =  " + str(mlanmax2) )
                logging.info("MbsLandscape: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 3
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("MbsLandscape: interval =  " + str(eqint2) )
                logging.info("MbsLandscape: range =  " + str(mrange) )

                cls1 = mlanmin2 + eqint2
                cls3 = mlanmin2 + eqint2 + eqint2

                updateFields = ("MbsLandscape", "MbsLaClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= cls1):
                            row[1] = 1
                        elif (row[0] >= cls3) :
                            row[1] = 3
                        elif (row[0] > cls1 and row[0]  < cls3) :
                            row[1] = 2
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("MbsLandscape: no members present in 'landscape' travel distance" )


            outStatsTable = "stats_county_out_MX"
            statsFields = [["MbsCounty", "MIN"],["MbsCounty", "MAX"]]
            arcpy.Statistics_analysis(intabepr, outStatsTable, statsFields)

            mlanmin = arcpy.da.SearchCursor("stats_county_out_MX",("MIN_MbsCounty",)).next()[0]
            if mlanmin:
                mlanmin2 = int(mlanmin)
                mlanmin3 = '{0:,}'.format(mlanmin2)
                logging.info("MbsCounty: Min =  " + str(mlanmin2) )
                logging.info("MbsCounty: Min =  " + str(mlanmin3) )

                mlanmax = arcpy.da.SearchCursor("stats_county_out_MX",("MAX_MbsCounty",)).next()[0]
                mlanmax2 = int(mlanmax)
                mlanmax3 = '{0:,}'.format(mlanmax2)
                logging.info("MbsCounty: Max =  " + str(mlanmax2) )
                logging.info("MbsCounty: Max =  " + str(mlanmax3) )

                mrange = mlanmax2 - mlanmin2
                interval = 3
                eqint = mrange / interval
                eqint2 = int(eqint)
                logging.info("MbsCounty: interval =  " + str(eqint2) )
                logging.info("MbsCounty: range =  " + str(mrange) )

                cls1 = mlanmin2 + eqint2
                cls3 = mlanmin2 + eqint2 + eqint2

                updateFields = ("MbsCounty", "MbsCoClass")
                with arcpy.da.UpdateCursor("ReservesPoints", updateFields) as cursor:
                    for row in cursor:
                        if (row[0] != None and row[0] <= cls1):
                            row[1] = 1
                        elif (row[0] >= cls3) :
                            row[1] = 3
                        elif (row[0] > cls1 and row[0]  < cls3) :
                            row[1] = 2
                        else:
                            row[1] = 0
                        cursor.updateRow(row)
            else:
                logging.info("MbsCounty: no members present in 'county' travel distance" )


            mxd6.activeView = df.name
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            mxd6.activeView = df2.name
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            mxd6.saveACopy(os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '6ReservesMembers.mxd'))

            logging.info ("ArcMap 06 updated")



        if PDFs == 'true':
            logging.info ("PDFs to be exported")
            arcpy.AddMessage("    Saving PDFs")

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            map_file1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '1TypeofMembership.mxd')

            mxd1 = arcpy.mapping.MapDocument(map_file1)
            mxdname = mxd1.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd1.dataDrivenPages.pageCount + 1):
              mxd1.dataDrivenPages.currentPageID = pageNum
              name = str(mxd1.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd1, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
              pdf1 = exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf"
            del mxd1
            logging.info("PDF 01 saved")

            map_file2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '2DensityofMemberships.mxd')

            mxd2 = arcpy.mapping.MapDocument(map_file2)
            mxdname = mxd2.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd2.dataDrivenPages.pageCount + 1):
              mxd2.dataDrivenPages.currentPageID = pageNum
              name = str(mxd2.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd2, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
              pdf2 = exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf"
            del mxd2
            logging.info("PDF 02 saved")

            map_file3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '3DensityofMembers.mxd')
            mxd3 = arcpy.mapping.MapDocument(map_file3)
            mxdname = mxd3.filePath.split("\\")[-1]
            mxdname = mxdname.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd3.dataDrivenPages.pageCount + 1):
              mxd3.dataDrivenPages.currentPageID = pageNum
              name = str(mxd3.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd3, exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf", resolution = 450)
              pdf3 = exportPath+"\\"+ mxdname + str(pageNum)+ name + ".pdf"
            del mxd3
            logging.info("PDF 03 saved")

            map_file4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '4PercentageMembers.mxd')
            mxd4 = arcpy.mapping.MapDocument(map_file4)
            mxdname4 = mxd4.filePath.split("\\")[-1]
            mxdname4 = mxdname4.replace(".mxd" , "")
            exportPath = PDFloctn
            for pageNum in range(1, mxd4.dataDrivenPages.pageCount + 1):
              mxd4.dataDrivenPages.currentPageID = pageNum
              name = str(mxd4.dataDrivenPages.pageRow.NAME)
              arcpy.mapping.ExportToPDF(mxd4, exportPath+"\\"+ mxdname4 + str(pageNum)+ name + ".pdf", resolution = 450)
              pdf4 = exportPath+"\\"+ mxdname4 + str(pageNum)+ name + ".pdf"
            del mxd4
            logging.info("PDF 04 saved")

            if Reserves == 'true':

                map_file5 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '5ReservesPopulation.mxd')
                mxd5 = arcpy.mapping.MapDocument(map_file5)
                mxdname5 = mxd5.filePath.split("\\")[-1]
                mxdname5 = mxdname5.replace(".mxd" , "")
                pageNum = 1
                exportPath = PDFloctn
                arcpy.mapping.ExportToPDF(mxd5, exportPath+"\\"+ mxdname5 + str(pageNum)+ name + ".pdf", resolution = 450)
                pdf5 = exportPath+"\\"+ mxdname5 + str(pageNum)+ name + ".pdf"
                del mxd5
                logging.info("PDF 05 saved")

                map_file6 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '6ReservesMembers.mxd')
                mxd6 = arcpy.mapping.MapDocument(map_file6)
                mxdname6 = mxd6.filePath.split("\\")[-1]
                mxdname6 = mxdname6.replace(".mxd" , "")
                pageNum = 1
                exportPath = PDFloctn
                arcpy.mapping.ExportToPDF(mxd6, exportPath+"\\"+ mxdname6 + str(pageNum)+ name + ".pdf", resolution = 450)
                pdf6 = exportPath+"\\"+ mxdname6 + str(pageNum)+ name + ".pdf"
                del mxd6
                logging.info("PDF 06 saved")

            arcpy.AddMessage("    PDFs saved to " + PDFloctn)

            if fulltext == 'true':
                elapsed_time_seconds_tool1 = time.time() - start_time_t0
                mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
                ht1, mt1 = divmod(mt1, 60)
                timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
                messages.addMessage("        Progress time: " + str(timetaken))

            time.sleep(4)  # sleep time in seconds...

            os.startfile(pdf1)
            os.startfile(pdf2)
            os.startfile(pdf3)
            os.startfile(pdf4)

            if Reserves == 'true':

              os.startfile(pdf5)
              os.startfile(pdf6)

            arcpy.AddMessage("    Opening PDFs")

        else:
            arcpy.AddMessage(" ")


        if Aview1 == 'true':

            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Opening data in ArcMaps")

            map1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '1TypeofMembership.mxd')
            map2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '2DensityofMemberships.mxd')
            map3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '3DensityofMembers.mxd')
            map4 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '4PercentageMembers.mxd')
            map5 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '5ReservesPopulation.mxd')
            map6 = os.path.join(os.path.dirname(os.path.dirname(__file__)),'01ArcMaps', '6ReservesMembers.mxd')


            arcpy.AddMessage("    ArcMap  " + map1)
            arcpy.AddMessage("    ArcMap  " + map2)
            arcpy.AddMessage("    ArcMap  " + map3)
            arcpy.AddMessage("    ArcMap  " + map4)

            if Reserves == 'true':

              arcpy.AddMessage("    ArcMap  " + map5)
              arcpy.AddMessage("    ArcMap  " + map6)

            os.startfile(map1)
            os.startfile(map2)
            os.startfile(map3)
            os.startfile(map4)

            if Reserves == 'true':

              os.startfile(map5)
              os.startfile(map6)

            time.sleep(15)

            arcpy.AddMessage("    ArcMaps opened (one per map document)")

        else:
            arcpy.AddMessage(" ")


        DeleteS = "false"

        if DeleteS == 'true':

            delStringDX = "*_MX"
            allDX = arcpy.ListRasters(delStringDX)
            for rasterDX in allDX:
                 try:
                  arcpy.Delete_management(rasterDX)
                 except:
                  messages.addMessage("Can't delete " + str(rasterDX))

            allDX3 = arcpy.ListTables(delStringDX)
            for TableDX in allDX3:
                 try:
                  arcpy.Delete_management(TableDX)
                 except:
                  messages.addMessage("Can't delete " + str(TableDX))

            allDX4 = arcpy.ListFeatureClasses(delStringDX)
            for FeatDX in allDX4:
                 try:
                  arcpy.Delete_management(FeatDX)
                 except:
                  messages.addMessage("Can't delete " + str(FeatDX))

            arcpy.AddMessage("    Scratch data deleted")

        else:
            arcpy.AddMessage(" ")

        elapsed_time_seconds_tool1 = time.time() - start_time_t0
        mt1, st1 = divmod(elapsed_time_seconds_tool1, 60)
        ht1, mt1 = divmod(mt1, 60)
        timetaken =  "%d hours %02d minutes %02d seconds" % (ht1, mt1, st1)
        logging.info( "Analysis completed")
        logging.info("Progress time: " + str(timetaken))

        arcpy.AddMessage("    Analysis completed")
        arcpy.AddMessage(" ")
        logging.shutdown()
        logging.getLogger(None).handlers =[]

        return
