# cubifySvalbard
A little side project to my thesis using the arcpy module - gridding ICESat-2 elevation changes over glaciers in Svalbard. Thesis project is in the repository SvalbardSurges. **Necessary to have an active ArcGIS licence :(** and arcpy installed.

![cubify austfonna](https://github.com/user-attachments/assets/4f03947a-ed75-45a8-bc9a-a4df26606e36)

## Documentation
Set workspace and paths, set cell size (variable cubesize) of grid.

![image](https://github.com/user-attachments/assets/e57f30ae-4a97-42b0-bb8e-eb22807cf79c)

Script works with results produced by SvalbardSurges (my thesis - possible to download in the SvalbardSurges repository), creates a fishnet based on the specified cell size, fills the grid with the average elevation change measured by ICESat-2 for each cell. Utilizes ArcGIS functions. Creates a grid for each glacier separately  (saved as geopackage), then merges the result for the whole archipelago. Result is saved for each year as a .tif raster and a .geojson (not recommended to use - too big for handling). 



