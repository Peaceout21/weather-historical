import gdal
import numpy as np
import gzip, shutil, os
import argparse
import zipfile

def create_vrt(dat_file, vrt_file):
    simple_source = '<VRTDataset rasterXSize="%i" rasterYSize="%i">' % (3600, 1200) + \
                    '<VRTRasterBand dataType="CFloat32" band="1" subClass="VRTRawRasterBand">' + \
                    '<SourceFilename relativeToVRT="1">%s</SourceFilename>' % dat_file + \
                    '<ImageOffset>0</ImageOffset>' + \
                    '<PixelOffset>4</PixelOffset>' + \
                    '<LineOffset>14400</LineOffset>' + \
                    '</VRTRasterBand>' + \
                    '</VRTDataset>'
    with open(f"{vrt_file}", "w") as text_file:
        text_file.write(simple_source)
    return 1

def create_tif_from_raster(source_vrt, dest_tif, rectified_dest_tif = None):
    os.system(f"gdal_translate -ot Float32 -of GTiff -a_srs EPSG:4326 -a_ullr 0 60 360 -60  {source_vrt} {dest_tif}")
    # os.system(f"gdalwarp -t_srs WGS84 {dest_tif} {rectified_dest_tif} -wo SOURCE_EXTRA=10000 --config CENTER_LONG 0")
    return 1

if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument("--file", "-f", type = str, required = True)
    args = parser.parse_args()
    zip_raw_file_name = args.file
    raw_file_name = zip_raw_file_name.replace('.gz', '')
    VRT_file_name = raw_file_name.replace('.dat', '.vrt')
    TIF_file_name = VRT_file_name.replace('.vrt', '.tif')
    print(zip_raw_file_name, raw_file_name, VRT_file_name, TIF_file_name)

    if  zipfile.is_zipfile(raw_file_name):
        with gzip.open(zip_raw_file_name, 'rb') as f_in:
            with open(raw_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    #### virtual raster file creation 
    create_vrt(raw_file_name, VRT_file_name )
    #### convert virtual raster to tif
    create_tif_from_raster(VRT_file_name, VRT_file_name.replace('.vrt', '.tif'))
    