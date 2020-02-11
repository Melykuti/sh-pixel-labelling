from sentinelhub import WcsRequest, BBox, CRS, MimeType, CustomUrlParam, get_area_dates, DataSource
from datetime import datetime, timedelta
import json, time
import numpy as np
import pandas as pd
from utils.utils import pairs_to_rows, read_out_pixels

def SH_TCI_retrieve(loc_dict, INSTANCE_ID, LAYER_NAME_TCI, DATA_SOURCE):
    '''
    SH = Sentinel Hub, TCI = True Colour Image
    https://sentinelhub-py.readthedocs.io/en/latest/examples/ogc_request.html#WCS-request
    https://sentinelhub-py.readthedocs.io/en/latest/examples/ogc_request.html#Data-Sources  for L2A
    loc_dict is the dictionary of a single targeted location.
    '''
    bbox_coords_wgs84 = [loc_dict['bl'][0], loc_dict['bl'][1],\
        loc_dict['bl'][0]+loc_dict['sl'][0], loc_dict['bl'][1]+loc_dict['sl'][1]]
    # c[0]-long, c[1]-lat, c[0]+long, c[1]+lat
    bounding_box = BBox(bbox=bbox_coords_wgs84, crs=CRS.WGS84)

    wcs_true_color_request = WcsRequest(data_source=DATA_SOURCE,
                                    layer=LAYER_NAME_TCI,
                                    bbox=bounding_box, 
                                    time=(loc_dict['date'], loc_dict['date']),
                                    resx='10m', resy='10m',
                                    image_format=MimeType.PNG,
                                    instance_id=INSTANCE_ID,
                                    custom_url_params={CustomUrlParam.SHOWLOGO: False})
    wcs_true_color_imgs = wcs_true_color_request.get_data()
    available_dates = wcs_true_color_request.get_dates()
    return wcs_true_color_imgs, available_dates

def SH_TCI_retrieve_successor(loc_dict, INSTANCE_ID, LAYER_NAME_TCI, DATA_SOURCE):
    '''
    SH = Sentinel Hub, TCI = True Colour Image
    https://sentinelhub-py.readthedocs.io/en/latest/examples/ogc_request.html#WCS-request
    https://sentinelhub-py.readthedocs.io/en/latest/examples/ogc_request.html#Data-Sources  for L2A
    loc_dict is the dictionary of a single targeted location.
    This finds the first image on or following the day that is inputted. It returns the images and their dates
     of acquisition.
    '''
    bbox_coords_wgs84 = [loc_dict['bl'][0], loc_dict['bl'][1],\
        loc_dict['bl'][0]+loc_dict['sl'][0], loc_dict['bl'][1]+loc_dict['sl'][1]]
    # c[0]-long, c[1]-lat, c[0]+long, c[1]+lat
    bounding_box = BBox(bbox=bbox_coords_wgs84, crs=CRS.WGS84)
    start_date = loc_dict['date']
    end_date = start_date
    available_dates = list()
    passed_today = False

    while len(available_dates)==0 and passed_today==False:
        end_date = datetime.strftime(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(5), '%Y-%m-%d')
        passed_today = datetime.strptime(end_date, '%Y-%m-%d') > datetime.today()
        wcs_true_color_request = WcsRequest(data_source=DATA_SOURCE,
                                    layer=LAYER_NAME_TCI,
                                    bbox=bounding_box, 
                                    time=(start_date, end_date),
                                    resx='10m', resy='10m',
                                    image_format=MimeType.PNG,
                                    instance_id=INSTANCE_ID,
                                    custom_url_params={CustomUrlParam.SHOWLOGO: False})
        available_dates = wcs_true_color_request.get_dates()
    wcs_true_color_imgs = wcs_true_color_request.get_data()
    return wcs_true_color_imgs, available_dates

def SH_bands_retrieve(loc_dict, bands_script, INSTANCE_ID, LAYER_NAME_BANDS, DATA_SOURCE):
    '''
    loc_dict is the dictionary of a single targeted location.
    '''
    bbox_coords_wgs84 = [loc_dict['bl'][0], loc_dict['bl'][1],\
        loc_dict['bl'][0]+loc_dict['sl'][0], loc_dict['bl'][1]+loc_dict['sl'][1]]
    # c[0]-long, c[1]-lat, c[0]+long, c[1]+lat
    bounding_box = BBox(bbox=bbox_coords_wgs84, crs=CRS.WGS84)

    wcs_bands_request = WcsRequest(data_source=DATA_SOURCE,
                                    layer=LAYER_NAME_BANDS,
                                    bbox=bounding_box, 
                                    time=(loc_dict['date'], loc_dict['date']),
                                    resx='10m', resy='10m',
                                    image_format=MimeType.TIFF_d32f,
                                    instance_id=INSTANCE_ID,
                                    custom_url_params={CustomUrlParam.EVALSCRIPT: bands_script, CustomUrlParam.SHOWLOGO: False})
    wcs_bands = wcs_bands_request.get_data()
    return wcs_bands

def download_pixel_vectors(source_path, bands_of_interest, bands_script, INSTANCE_ID,
                     LAYER_NAME_BANDS, DATA_SOURCE):
    '''
    Downloads all images that are specified in JSON file of selected pixels and retrieves
    selected pixels' intensity values.
    '''
    start_time = time.time()
    M_list = list()
    date_list = list()
    label_list = list()

    with open(source_path, 'r') as source_file:
        json_dict = json.loads(source_file.read())

    for l in json_dict:
        print(l)
        json_dict[l]['px'] = np.array(pairs_to_rows(json_dict[l]['px']))
        wcs_bands = SH_bands_retrieve(json_dict[l], bands_script, INSTANCE_ID,
                     LAYER_NAME_BANDS, DATA_SOURCE)
        if len(wcs_bands)>0:
            M_list.append(pd.DataFrame(read_out_pixels(wcs_bands[0], json_dict[l], bands_of_interest), dtype=np.uint16))
            date_list.append(pd.Series([l]*json_dict[l]['px'].shape[1]))
            label_list.append(pd.Series(np.full(json_dict[l]['px'].shape[1], json_dict[l]['label']), dtype=np.float32))

    Mdf = pd.concat(M_list, axis=0, ignore_index=True)
    Mdf.columns = bands_of_interest
    Mdf = Mdf.assign(date = pd.concat(date_list, ignore_index=True))
    Mdf = Mdf.assign(label = pd.concat(label_list, ignore_index=True))

    print('Time elapsed: {:.2f} sec.'.format(time.time() - start_time))
    return Mdf
