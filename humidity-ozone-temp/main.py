import gdal
import rasterio
import numpy as np
import os
import glob


def tif_convert(opfilename, rlayer):
    EPSG = '-a_srs EPSG:4326 -a_nodata -32768 -co "COMPRESS=PACKBITS"'
    translateOptionText = EPSG+" -a_ullr " + "-180" + " " + "90" + " " + "180" + " " + "-90"
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
    gdal.Translate(f'{opfilename}.tif',rlayer, options=translateoptions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("--file", "-f", type = str, required = True)
    args = parser.parse_args()
    raw_file_name = args.file
    
    ds = gdal.Open(raw_file_name, gdal.GA_ReadOnly)

    #creating tifs of all subdatasets
    for i in [887, 889, 890, 839, 841, 842, 253,255,256, 863,865,866]:
        
        subhdflayer = ds.GetSubDatasets()[i][0]
        rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
        opfilename = subhdflayer.split(':')[4]
        ''' this converts each sub dataset layer to a tiff '''
        tif_convert(opfilename, rlayer)

    #converting the tifs into cogs 
    # for tif in tifs:
    #     name = tif.split('/')[4].split('.')[0]
    #     root = '/Users/manyachadha/weather'
    #     os.system("gdal_translate {}/{}.tif {}/{}_stack_COG.tif -co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co COMPRESS=LZW -co PREDICTOR=2 -co COPY_SRC_OVERVIEWS=YES -co BIGTIFF=YES".format(root,name,root,name))
        

    #stacking the cogs to create a single tif
    # root = "/Users/manyachadha/weather"
    # cogs = glob.glob("/Users/manyachadha/weather/*COG.tif")

    tifs = glob.glob("*.tif")
    for tif in tifs:
        name = tif.split("/")[4].split(".")[0]
        with rasterio.open(tifs[0]) as src0:
                    meta = src0.meta
        meta.update(count = len(tifs))
        with rasterio.open('stack.tif', 'w', **meta) as dst:
            for id, layer in enumerate(tifs, start = 1):
                with rasterio.open(layer) as src1:
                            dst.write_band(id, src1.read(1))

    #convering the final stacked tif into a cog

    os.system("gdal_translate stack.tif stack_COG.tif -co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co COMPRESS=LZW -co PREDICTOR=2 -co COPY_SRC_OVERVIEWS=YES -co BIGTIFF=YES")

    for i in glob.glob("/Users/manyachadha/weather/*"):
        if not i.endswith("stack_COG.tif"):
            os.remove(i)

