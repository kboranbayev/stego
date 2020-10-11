#!/usr/bin/python3
"""

@name           utils.py

@topic          Steganography

@author         Kuanysh Boranbayev

@date           October 11, 2020

@description    This utility module that has two main functions:
                Encode - handles encoding an image into another image
                Decode - handles decoding an image from another image
                This module also uses encryption and decryption functions from feistel.py.
                
@version        1.0
"""
import numpy as np
from PIL import Image
from bitstring import BitArray
import binascii, feistel

STEGO_FILENAME = "f1l3#@m3"

STEGO_KEY = "$t3g0"

IMG_W = "IMG_W"
IMG_H = "IMG_H"


def DecToBin(n): 
    binary = 0
    ctr = 0
    temp = n  #copying number
    
    #calculating binary
    while(temp > 0):
        binary = ((temp%2)*(10**ctr)) + binary
        temp = int(temp/2)
        ctr += 1
    
    data = str(binary)
    
    if len(str(binary)) < 8:
        n0 = 8 - len(str(binary))
        for i in range(0,n0):
            data = '0' + data 
        
    return data
    

def Encode (carrierImagePath, targetImagePath, dest, key):
    cimg = Image.open(carrierImagePath, 'r')
    
    timg = Image.open(targetImagePath, 'r')
    
    b_data = ""
    numChars = 0

    n_arr = np.array(list(timg.getdata()))

    encrypted = feistel.encrypt(n_arr.flatten(), key)

    filename = targetImagePath

    w, h = timg.size

    width, height = cimg.size
    
    array = np.array(list(cimg.getdata()))
    
    if cimg.mode == 'RGB':
        print("RGB mode")
        n = 3
        m = 0
    elif cimg.mode == 'RGBA':
        print("RGBA mode")
        n = 4
        m = 1
        
    total_pixels = array.size//n
    
    # construct stego medium
    stego_medium = ""
    
    stego_medium += targetImagePath
    stego_medium += STEGO_FILENAME
    stego_medium += str(w)
    stego_medium += IMG_W
    stego_medium += str(h)
    stego_medium += IMG_H

    # adding filename + STEGO_DELIM
    b_message = ''.join([format(ord(i), "08b") for i in stego_medium])
    
    # adding data
    b_message += encrypted

    # adding stego key
    b_message += ''.join([format(ord(i), "08b") for i in STEGO_KEY])
    
    req_pixels = len(b_message)
    
    if req_pixels > total_pixels:
        print("ERROR: Need larger file size")
        return "ERROR: Need larger file size"
    else:
        index = 0
        for p in range(total_pixels):
            for q in range(m, n):
                if index < req_pixels:
                    array[p][q] = int(bin(array[p][q])[2:9] + b_message[index],2)
                    index += 1
        
        array2 = array.reshape(height, width, n)
        
        enc_img = Image.fromarray(array2.astype('uint8'), cimg.mode)
        enc_img.save(dest)
    
        print("W = ", w, " H = ", h)
        print("Total Data Bytes: ", len(n_arr))
        print("Image Encoded Successfully")

    return "Success"
        
def Decode(src, dest, key):
    img = Image.open(src, 'r')
    array = np.array(list(img.getdata()))
    width, height = img.size

    if img.mode == 'RGB':
        n = 3
        m = 0
    elif img.mode == 'RGBA':
        n = 4
        m = 1

    total_pixels = array.size//n

    hidden_bits = ""

    for p in range(total_pixels):
        for q in range(m, n):
            hidden_bits += (bin(array[p][q])[2:][-1])

    bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    filename = ""
    
    hidden_data = ""
    
    b_bits = []
    for i in range(len(bits)):
        if hidden_data[-8:] == STEGO_FILENAME:
            filename = hidden_data[:-8]
            hidden_data = ""
            b_bits = []
        if hidden_data[-5:] == IMG_W:
            w = hidden_data[:-5]
            hidden_data = ""
            b_bits = []
        if hidden_data[-5:] == IMG_H:
            h = hidden_data[:-5]
            hidden_data = ""
            b_bits = []
        if hidden_data[-5:] == STEGO_KEY:
            b_bits = b_bits[:-5]
            break
        else:
            hidden_data += chr(int(bits[i], 2))
            b_bits.append(int(bits[i], 2))

    decrypted = feistel.decrypt(b_bits, key)
    
    if STEGO_KEY in hidden_data:
        print("Filename: ", filename)
        print("W = ", w, " H = ", h)
        print("Total Bytes: ", len(b_bits), " (not counting BMP headers) ")

        A = np.array(decrypted)
        A2 = A.reshape(int(h),int(w), 3)

        dec_img = Image.fromarray(A2.astype('uint8'), img.mode)
        dec_img.save(dest)
    else:
        print("No Hidden Message Found")
        return "No Hidden Message Found"

    return "Success"