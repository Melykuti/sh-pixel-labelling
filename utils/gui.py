# This is the code to define the graphical user interface (GUI) with Tkinter

from datetime import datetime, timedelta
import json
import numpy as np
import os
from PIL import Image, ImageTk
import tkinter as tk
from utils.downloading import SH_TCI_retrieve_successor
from utils.utils import rows_to_pairs, consolidate_name

class ImagePanel(tk.Canvas):
    def __init__(self, master, img):
        #self.grid(row=0, column=0)
        hei, wid = img.shape[0], img.shape[1]
        self.width=master.magnification*wid
        self.height=master.magnification*hei
        tk.Canvas.__init__(self, master, width=self.width, height=self.height)
        self.bind("<Button-1>", self.pixelclick)
        self.img_orig = img
        self.draw_image(self.img_orig, self.master.pxs)

    def draw_image(self, img_orig, l):
        if len(l)>0:
            img = img_orig.copy()
            for px in l:
                # Black:
                #img[px[0], px[1], :] = 0
                # Magenta:
                #img[px[0], px[1], 0] = 192
                #img[px[0], px[1], 1] = 0
                #img[px[0], px[1], 2] = 192
                img[px[0], px[1], 0] = self.master.colour_for_selection[0]
                img[px[0], px[1], 1] = self.master.colour_for_selection[1]
                img[px[0], px[1], 2] = self.master.colour_for_selection[2]
        else:
            img = img_orig.copy()

        img = np.kron(img, np.ones((self.master.magnification, self.master.magnification), dtype=np.uint8)[:,:,np.newaxis])
        self.imgPIL=ImageTk.PhotoImage(Image.fromarray(img))
        self.create_image((0, 0), image=self.imgPIL, anchor='nw', state="normal")

    def pixelclick(self, event):
        col, row = event.x//self.master.magnification, event.y//self.master.magnification
        #print("Clicked at row {0}, column {1}.".format(row, col))
        if [row, col] in self.master.pxs:
            self.master.pxs.remove([row, col])
        else:
            self.master.pxs.append([row, col])
        self.draw_image(self.img_orig, self.master.pxs)

class ButtonsPanel(tk.Frame):
    def __init__(self, master):
        frame = tk.Frame.__init__(self, master)
        #self.grid(row=0, column=1, sticky="s")
        self.createWidgets()
        return frame

    def createWidgets(self):
        self.skip = tk.Button(self, text="Skip", command=self.skp, padx=5)
        self.skip.grid(row=0)
        self.savencontinue = tk.Button(self, text="Save & Continue", command=self.snc)
        self.savencontinue.grid(row=1)
        self.savenquit = tk.Button(self, text="Save & Quit", command=self.snq, padx=2)
        self.savenquit.grid(row=2)
        self.cancel = tk.Button(self, text="Cancel", command=self.cnq, padx=4)
        self.cancel.grid(row=3)

    def skp(self):
        # active_date, next_date are strings in YYYY-MM-DD format

        active_date = self.master.location['date']
        print("Skipping " + active_date)

        # increment date by 1 day
        next_date = datetime.strftime(datetime.strptime(active_date, '%Y-%m-%d') + timedelta(1),
                     '%Y-%m-%d')
        self.master.location['date'] = next_date
        #local_location = self.master.location.copy()
        #local_location['date'] = next_date
        active_date = self.master.create_workspace(self.master, self.master.location)
        #active_date = self.master.create_workspace(self.master, local_location)
        self.master.location['date'] = active_date
        
    def snc(self):
        # active_date, next_date are strings in YYYY-MM-DD format

        active_date = self.master.location['date']
        print("Saving {0} & Continuing".format(active_date))
        self.master.locations_json[active_date] = self.master.location.copy()
        self.master.locations_json[active_date]['px'] = self.master.pxs.copy()
        self.savetofile()
        
        # increment date by 1 day
        next_date = datetime.strftime(datetime.strptime(active_date, '%Y-%m-%d') + timedelta(1), '%Y-%m-%d')
        self.master.location['date'] = next_date
        active_date = self.master.create_workspace(self.master, self.master.location)
        self.master.location['date'] = active_date

    def snq(self):
        # active_date is a string in YYYY-MM-DD format

        active_date = self.master.location['date']
        print("Saving {0} & Quitting".format(active_date))
        self.master.locations_json[active_date] = self.master.location.copy()
        self.master.locations_json[active_date]['px'] = self.master.pxs.copy()
        self.savetofile()
        self.master.destroy()

    def cnq(self):
        active_date = self.master.location['date']
        print("Cancel. Quitting without saving {0}.".format(active_date))
        self.master.destroy()
        
    def savetofile(self):
        if not os.path.exists(self.master.output_folder):
            os.makedirs(self.master.output_folder)
        # save dict of dates and pixels in JSON, named using locations[k]['name']
        with open(os.path.join(self.master.output_folder, consolidate_name(self.master.location['name']) + '_' + self.master.level_choice + '_locations.json'), 'w') as openfile:
            openfile.write(json.dumps(self.master.locations_json, ensure_ascii=False, indent=0))
        # Saving pixel intensity values will be done separately.

class BigFrame(tk.Tk):
    def __init__(self, location, INSTANCE_ID, LAYER_NAME_TCI, DATA_SOURCE, magnification, colour_for_selection, output_folder, level_choice):
        tk.Tk.__init__(self)
        # location['px'] (px) is an np.array of size (2 x nr_of_pixels). self.master.pxs is a list of pairs.
        self.location = location
        self.pxs = rows_to_pairs(location['px'])
        self.INSTANCE_ID = INSTANCE_ID
        self.LAYER_NAME_TCI = LAYER_NAME_TCI
        self.DATA_SOURCE = DATA_SOURCE
        self.magnification = magnification
        self.colour_for_selection = colour_for_selection
        self.output_folder = output_folder
        self.level_choice = level_choice

        self.canvas = tk.Canvas().grid(row=0, column=0)
        self.but = ButtonsPanel(master=self).grid(row=0, column=1)#, sticky="s")
        active_date = self.create_workspace(self, self.location)
        self.location['date'] = active_date
        self.locations_json = dict()

    def create_workspace(self, root, location):
        wms_true_color_imgs, available_dates = SH_TCI_retrieve_successor(location, self.INSTANCE_ID, self.LAYER_NAME_TCI, self.DATA_SOURCE)
        print('Next available dates: ', [datetime.strftime(ad, '%Y-%m-%d %H:%M:%S') for ad in available_dates])
        if len(available_dates)>0:
            img = wms_true_color_imgs[0]
            #px = location['px']
            self.imgpanel = ImagePanel(root, img).grid(row=0, column=0)
            #self.imgpanel = ImagePanel(root, img, px).grid(row=0, column=0)
            #self.imgpanel = ImagePanel(self.canvas, img, px, magnification, root.colour_for_selection).grid(row=0, column=0)
            return datetime.strftime(available_dates[0], '%Y-%m-%d')
        else:
            print('You reached the present.')
            #self.but.cnq()
            #self.bbb
            #self.destroy()
            root.destroy()

