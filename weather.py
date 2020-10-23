{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "#extract all subdatasets from h5 and convert them to tif \n",
    "#make all these tifs into cogs\n",
    "#stack all cogs and create a tif \n",
    "#oconvert final tif to COG"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import gdal\n",
    "import rasterio\n",
    "import numpy as np\n",
    "import os\n",
    "import glob\n",
    "from rasterio.mask import mask"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "ds = gdal.Open(\"Downloads/MYD08_D3.A2020289.061.2020291075457.hdf\", gdal.GA_ReadOnly)\n",
    "# ds.GetSubDatasets()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "#temp mean, min, max corr to 887, 889, 890\n",
    "#ozone mean, min, max corr to 839, 841, 842\n",
    "#cloud frac mean, min, max corr to 253, 255, 256\n",
    "#water vap mean, min, max corr to 863, 865, 866 "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'/Users/manyachadha/weather'"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "os.chdir(\"/Users/manyachadha/weather\")\n",
    "os.getcwd()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "def tif_convert(rlayer):\n",
    "    EPSG = '-a_srs EPSG:4326 -a_nodata -32768 -co \"COMPRESS=PACKBITS\"'\n",
    "    translateOptionText = EPSG+\" -a_ullr \" + \"-180\" + \" \" + \"90\" + \" \" + \"180\" + \" \" + \"-90\"\n",
    "    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))\n",
    "    gdal.Translate(f'{opfilename}.tif',rlayer, options=translateoptions)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "#creating tifs of all subdatasets\n",
    "for i in [887, 889, 890, 839, 841, 842, 253,255,256, 863,865,866]:\n",
    "    \n",
    "    subhdflayer = ds.GetSubDatasets()[i][0]\n",
    "    rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)\n",
    "    opfilename = subhdflayer.split(':')[4]\n",
    "    \n",
    "    tif_convert(rlayer)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "#converting the tifs into cogs \n",
    "tifs = glob.glob(\"/Users/manyachadha/weather/*.tif\")\n",
    "for tif in tifs:\n",
    "    name = tif.split('/')[4].split('.')[0]\n",
    "    root = '/Users/manyachadha/weather'\n",
    "    os.system(\"gdal_translate {}/{}.tif {}/{}_stack_COG.tif -co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co COMPRESS=LZW -co PREDICTOR=2 -co COPY_SRC_OVERVIEWS=YES -co BIGTIFF=YES\".format(root,name,root,name))\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "#stacking the cogs to create a single tif\n",
    "root = \"/Users/manyachadha/weather\"\n",
    "cogs = glob.glob(\"/Users/manyachadha/weather/*COG.tif\")\n",
    "for cog in cogs:\n",
    "    name = cog.split(\"/\")[4].split(\".\")[0]\n",
    "#     print(name)\n",
    "    with rasterio.open(cogs[0]) as src0:\n",
    "                meta = src0.meta\n",
    "    meta.update(count = len(cogs))\n",
    "    with rasterio.open(root + \"/stacked\" + '/stack.tif', 'w', **meta) as dst:\n",
    "        for id, layer in enumerate(cogs, start=1):\n",
    "            with rasterio.open(layer) as src1:\n",
    "                        dst.write_band(id, src1.read(1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#convering the final stacked tif into a cog\n",
    "root = \"/Users/manyachadha/weather\"\n",
    "os.system(\"gdal_translate {}/stacked/stack.tif {}/stacked/stack_COG.tif -co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co COMPRESS=LZW -co PREDICTOR=2 -co COPY_SRC_OVERVIEWS=YES -co BIGTIFF=YES\".format(root,root))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "metadata": {},
   "outputs": [],
   "source": [
    "for i in glob.glob(\"/Users/manyachadha/weather/*\"):\n",
    "    if i.endswith(\".xml\"):\n",
    "        os.remove(i)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
