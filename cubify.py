import arcpy
from pathlib import Path
import os
import geopandas as gpd
import numpy as np

# set workspace
arcpy.env.workspace = 'C:/Users/eliss/Documents/PGIS/cubify'
arcpy.env.overwriteOutput = 1

# paths
temppath = Path('weloveshapefiles/')
fishnetspath = Path('weloveshapefiles/fishnets/')
spatialjoinspath = Path('weloveshapefiles/spatialjoins/')
clipspath = Path('weloveshapefiles/clips/')
resultspath = Path('results/')

cubesize = 1000

directories = [temppath, fishnetspath, spatialjoinspath, clipspath, resultspath]


# ---------------------------------------------- FUNCTIONS ----------------------------------------------
def createDirectories(directories):
    for directory in directories:
        if not directory.exists():
            os.mkdir(directory)


def geopackages2shapefiles(glacier_ids, years):
    # loop through glacier ids and years and convert all geopackages to shapefiles

    for glacier_id in glacier_ids:
        # convert glacier polygon
        gpkg = gpd.read_file(f'C:/Users/eliss/Documents/diplomka/data/temp/glaciers/{glacier_id}.gpkg')
        gpkg.to_file(f'weloveshapefiles/{glacier_id}.shp')

        # convert icesat points for each year
        for year in years:
            gpkg = gpd.read_file(f'C:/Users/eliss/Documents/diplomka/data/temp/glaciers/{glacier_id}_{year}.gpkg')
            gpkg.to_file(f'weloveshapefiles/{glacier_id}_{year}.shp')


def cubify(glacier_ids, years):
    # create fishnet, spatial join and clip result to glacier extent

    i = 1
    for glacier_id in glacier_ids:
        print(f'{i}/{total}')
        i =i+1

        # open glacier polygon description
        glacier_description = arcpy.Describe(str(temppath / f'{glacier_id}.shp'))
        extent = glacier_description.extent

        for year in years:

            # create fishnet
            fishnet_outpath = str(Path(temppath / f'{glacier_id}_{year}_fishnet.shp'))

            if not Path(fishnet_outpath).is_file():
                arcpy.management.CreateFishnet(
                    out_feature_class=fishnet_outpath,  # set output feature class
                    origin_coord=f'{extent.XMin} {extent.YMin}',  # set coordinates of origin
                    y_axis_coord=f'{extent.XMin} {extent.YMin + 1}',  # set direction of y-axis
                    cell_width=cubesize,
                    cell_height=cubesize,
                    number_rows=None,
                    number_columns=None,
                    labels="NO_LABELS",
                    template=extent,
                    geometry_type="POLYGON"
                )

            # spatial join
            spatialjoin_outpath = str(Path(temppath / f'{glacier_id}_{year}_spatialjoin.shp'))
            if not Path(spatialjoin_outpath).is_file():
                arcpy.analysis.SpatialJoin(
                    target_features=fishnet_outpath,
                    join_features=str(Path(temppath / f'{glacier_id}_{year}.shp')),
                    out_feature_class=spatialjoin_outpath,
                    join_operation="JOIN_ONE_TO_MANY",
                    join_type="KEEP_ALL",
                    field_mapping=f'dh "dh" true true false 24 Double 0 0,Mean,#,{glacier_id}_{year},dh,-1,-1',
                    match_option="INTERSECT",
                    search_radius=None,
                    distance_field_name="",
                    match_fields=None
                )

            # clip
            clip_outpath = str(Path(temppath) / f'{glacier_id}_{year}_clip.shp')
            if not Path(clip_outpath).is_file():
                arcpy.analysis.Clip(
                    in_features=spatialjoin_outpath,
                    clip_features=str(temppath / f'{glacier_id}.shp'),
                    out_feature_class=clip_outpath,
                    cluster_tolerance=None
                )

# ----------------------------------------- SCRIPT --------------------------------------------------------

# get unique glacier ids, set unique years
data = gpd.read_file('C:/Users/eliss/Documents/diplomka/data/temp/svalbard_features.gpkg')
glacier_ids = np.unique(data.glacier_id)
years = [2020, 2021, 2022, 2023]
total = len(glacier_ids)

# loop through glaciers and CONVERT geopackages to shapefiles
#geopackages2shapefiles(glacier_ids, years)

# loop through glaciers and CUBIFY each glacier/year
cubify(glacier_ids, years)

# merge all the glaciers for all the years
for year in years:

    input_string = ''
    for glacier_id in glacier_ids:

        # if it doesn't exist --> continue
        if not Path(f'weloveshapefiles/{glacier_id}_{year}_clip.shp').is_file():
            continue

        # if type is not Polygon (for whatever reason) --> continue
        glacier_description = arcpy.Describe(f'weloveshapefiles/{glacier_id}_{year}_clip.shp')
        if glacier_description.shapeType != 'Polygon':
            continue

        # if everything is okay --> append to string
        input_string += f'weloveshapefiles/{glacier_id}_{year}_clip.shp;'

    input_string = input_string[:-1]
    # merge glacier fishnets for given year into one shapefile
    arcpy.management.Merge(
        inputs=input_string,
        output=f'results/cubifysvalbard{year}.geojson'
    )

    # convert fishnet to raster
    fishnet_clipped_path = f'results/cubifysvalbard{year}.shp'
    arcpy.conversion.PolygonToRaster(
        in_features=fishnet_clipped_path,
        value_field="dh",
        out_rasterdataset=f"results/cubifysvalbard{year}.tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=cubesize,  # same as fishnet
        build_rat="BUILD"
    )

# create project
aprx = arcpy.aprx()

# add layers of merged fishnets as rasters for each year

# set raster symbology

# create a map

# export map
