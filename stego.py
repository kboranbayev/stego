#!/usr/bin/python3
"""

@name           stego.py

@topic          Data Communication Applications - Steganography

@author         Kuanysh Boranbayev

@date           October 11, 2020

@description    This is GUI application for the steganography program. 
                This application uses Tkinter GUI framework built into Python.
                This application currently only supports image files with .BMP extension.
                To run the application simply enter the following command to the console:
                python stego.py

@modules        utils.py    - handles main encoding and decoding part of the application.
                feistel.py  - handles main encrypting and decrypting part of the application.

@version        1.0
"""
import utils
from tkinter import filedialog, Toplevel, Text, Tk, Label, Button, StringVar, END, W, E, HORIZONTAL
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image

APP_TITLE = "Steganography"
APP_MSG = "LSB Stego by Kuanysh Boranbayev"

OUTPUT_PLACEHOLDER = "Output file name (e.g.: encoded.bmp)"
KEY_PLACEHOLDER = "Enter secret key"

BTN_CARRIER_IMG = "Carrier/Encoded Image"
BTN_TARGET_IMG = "Target Image"

OPT_C = "carrier"
OPT_T = "target"

BTN_ENC = "Encode"
BTN_DEC = "Decode"

ERR_C = "Error: Carrier Image"
ERR_C_MSG = "Please select carrier image"
ERR_T = "Error: Target Image"
ERR_T_MSG = "Please select target image"
ERR_O = "Error: Output File Name"
ERR_O_MSG = "Please enter output file name"
ERR_K = "Error: Secret Key"
ERR_K_MSG = "Please enter secret key"

class Steganography:
    def __init__(self, master):
        self.master = master
        master.title(APP_TITLE)

        self.carrier_image_path = None
        self.target_image_path = None
        self.output_filename = None
        self.key = None

        self.message = APP_MSG
        self.label_text = StringVar()
        self.label_text.set(self.message)
        self.label = Label(master, textvariable=self.label_text)

        self.entry = Text(master, height=1, width=36)
        self.entry.insert(END, OUTPUT_PLACEHOLDER)
        self.key_entry = Text(master, height=1, width=36)
        self.key_entry.insert(END, KEY_PLACEHOLDER)

        self.select_carrier_img = Button(master, text=BTN_CARRIER_IMG, command= lambda: self.open_carrier_img(BTN_CARRIER_IMG))
        self.select_target_img = Button(master, text=BTN_TARGET_IMG, command= lambda: self.open_target_img(BTN_TARGET_IMG))

        self.encode_btn = Button(master, text=BTN_ENC, command=self.Encode)
        self.decode_btn = Button(master, text=BTN_DEC, command=self.Decode)

        self.label.grid(row=0, column=0, columnspan=3)

        self.select_carrier_img.grid(row=2, column=0, padx=10, pady=10)
        self.select_target_img.grid(row=2, column=1, padx=10, pady=10)
        self.entry.grid(row=2, column=2, padx=10, pady=10)
        
        self.encode_btn.grid(row=3, column=0)
        self.decode_btn.grid(row=3, column=1)
        self.key_entry.grid(row=3, column=2, padx=10, pady=10)

    # handle user inputs
    def get_user_input(self):
        self.output_filename = self.entry.get(1.0, END+"-1c")
        self.key = self.key_entry.get(1.0, END+"-1c")
        if self.carrier_image_path == None:
            self.popupmsg(ERR_C, ERR_C_MSG)
        elif self.target_image_path == None:
            self.popupmsg(ERR_T, ERR_T_MSG)
        elif self.output_filename == OUTPUT_PLACEHOLDER:
            self.popupmsg(ERR_O, ERR_O_MSG)
        elif self.key == KEY_PLACEHOLDER:
            self.popupmsg(ERR_K, ERR_K_MSG)
        
        print("User chosen output file name: ", self.output_filename)
        print("Secret key: ", self.key)
        
        return self.output_filename

    # Opens a selected carrier image
    # @param title - String title for the widget
    def open_carrier_img(self, title):
        global cimg

        cimg_root = Toplevel(self.master)
        
        cimg_root.title(title)

        cimg_root.filename = filedialog.askopenfile(initialdir = ".", title = "Select an image", filetypes = (("bmp files", "*.bmp"), ("all files", "*") ))
        cimg_path_label = Label(cimg_root, text = cimg_root.filename.name).pack()
        
        cimg = ImageTk.PhotoImage(Image.open(cimg_root.filename.name))
        
        cimg_label = Label(cimg_root, image = cimg).pack()

        self.carrier_image_path = cimg_root.filename.name

    # Opens a selected target image
    # @param title - String title for the widget
    def open_target_img(self, title):
        global timg

        timg_root = Toplevel(self.master)
        
        timg_root.title(title)

        timg_root.filename = filedialog.askopenfile(initialdir = ".", title = "Select an image", filetypes = (("bmp files", "*.bmp"), ("all files", "*") ))
        timg_path_label = Label(timg_root, text = timg_root.filename.name).pack()
        
        timg = ImageTk.PhotoImage(Image.open(timg_root.filename.name))
        
        timg_label = Label(timg_root, image = timg).pack()

        self.target_image_path = timg_root.filename.name


    # Encode method
    def Encode(self):
        self.get_user_input()
    
        result = utils.Encode(self.carrier_image_path, self.target_image_path, self.output_filename, self.key)

        if result == "Success":
            self.popupmsg("Success", "The image has been encoded successfully!")
        else:
            self.popupmsg("Failed", result)

    # Decode method
    def Decode(self):
        self.get_user_input()
        
        result = utils.Decode(self.carrier_image_path, self.output_filename, self.key)

        if result == "Success":
            self.popupmsg("Success", "The image has been decoded successfully!")
        else:
            self.popupmsg("Failed", result)

    # Pop-up message display
    # @param title - title for the message widget
    # @param msg - message text
    def popupmsg(self, title, msg):
        popup = Tk()
        popup.wm_title(title)
        label = Label(popup, text=msg)
        label.pack(side="top", fill="x", padx=70)
        B1 = Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()

root = Tk()
gui = Steganography(root)
root.mainloop()