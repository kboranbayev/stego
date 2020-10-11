#!/usr/bin/python3
"""

@name           feistel.py

@topic          Cryptography and Cryptanalysis

@author         Kuanysh Boranbayev

@date           March 5, 2020

@description    The program is designed to Encrypt and Decrypt a plaintext and an image file, namely .bmp image files 
                following 8-round Feistel Cipher.
                Application will accept following arguments:
                -h          to show the usage of the application
                -k          to supply key entered by keyboard
                -f          to supply key file
                -e          to encrypt
                -d          to decrypt
                -m          to indicate image file (.bmp)
                -t          to supply plaintext from the keyboard
                -i          to supply input file
                -o          to supply output file
                
@version        2.0
"""

import sys, getopt, os, random, string, binascii
from prettytable import PrettyTable
from bitstring import BitStream, BitArray
from tqdm import tqdm

def main (argv):
    plaintextFile = None
    ciphertextFile = None
    outputFile = None
    text = None

    usage = "Usage: " + sys.argv[0] + "\n[-k <Key> | -f <Key File Name>]\n[-d <Decrypt> | -e <Encrypt>]\n[-t <Plaintext | Ciphertext> | -i <Input File Name>]\n[-o <Output File Name>]"
    
    key = None
    keyFile = None
    encrypt = True
    mode = False
    
    try:
        opts, args = getopt.getopt (argv, "hdek:f:t:i:o:m:")
    except getopt.getoptError:
        sys.exit(1)

    if (len(sys.argv) < 8):
        print (usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':   # Help
            print (usage)
            sys.exit(2)
        elif opt == '-k': # Key by Keyboard
            key = arg
        elif opt == '-f': # Key by File
            keyFile = arg
        elif opt == '-d': # Decrypt Selected
            encrypt = False
        elif opt == '-m': # Decrypt Selected
            mode = True
        elif opt == '-t': # Plaintext by Keyboard
            text = arg
        elif opt == '-i': # Input by File
            if (encrypt): # Input File is Plaintext
                plaintextFile = arg
            else:         # Input File is Ciphertext  
                ciphertextFile = arg
        elif opt == '-o':
            outputFile = arg
    
    # DEMO-START
    # encrypted = encryptText (text, outputFile, key)
    # decrypted = decryptText (encrypted, outputFile, key)
    # DEMO-END
    
    if (key == None):
        key = readTextFile (keyFile)
    else:
        writeTextFile (key, "key")
    
    if (plaintextFile != None and mode):
        text = readImageFile (plaintextFile)
    elif (ciphertextFile != None and mode):
        text = readImageFile (ciphertextFile)
    elif (plaintextFile != None and not mode):
        text = readTextFile (plaintextFile)
    elif (ciphertextFile != None and not mode):
        text = readTextFile (ciphertextFile)
    
    if (encrypt):
        encrypted = encryptText (text, outputFile, key, mode)
        getAvalancheEffect (text, encrypted, mode)
    elif (not encrypt):
        decrypted = decryptText (text, outputFile, key, mode)
        getAvalancheEffect (decrypted, text, mode)
    else:
        print ("Something went wrong!\n")
    

def getAvalancheEffect (pt, ct, mode):
    sumChangedBits = 0
    results = PrettyTable()
    
    print ("\t\tAvalanche Effect")
    
    if (mode):
        pb = ""
        for i in range(len(pt)):
            pb += '{0:08b}'.format(pt[i], 'b')
        cb = ""
        for j in range(len(ct)):
            cb += '{0:08b}'.format(ct[j], 'b')
        
        for i in range(len(pb)):
            sumChangedBits += int(pb[i],2) ^ int(cb[i],2)

        results.field_names = ["Total Bits", "Total Changed Bits", "Overall Percentage"]
        results.add_row([len(pb), sumChangedBits, sumChangedBits * 100 / len(pb)])
    else:
        pb = make_bitseq(pt)
        cb = make_bitseq(ct)
        for i in range(len(pb)):
            sumChangedBits += int(pb[i],2) ^ int(cb[i],2)
        results.field_names = ["Ciphertext", "Plaintext", "Total Bits", "Total Changed Bits", "Overall Percentage"]
    
        results.add_row([ct, pt, len(pb), sumChangedBits, sumChangedBits * 100 / len(pb)])

    print (results)
    
# encrypts a plaintext
def encryptText (text, outputFile, key, mode):
    print ("\t\tEncrypting")
        
    L = [""] * (9)
    R = [""] * (9)

    
    if (mode):
        ciphertext = bytearray()
        for i in tqdm(range(len(text))):
            bit8 = '{0:08b}'.format(text[i], 'b')
            L[0] = bit8[:len(bit8)//2]
            R[0] = bit8[len(bit8)//2:]
            for j in range (1, 9):
                L[j] = R[j - 1]
                R[j] = XOR(L[j - 1], f(R[j - 1], j, key))
            ciphertext.append(ord(chr(int(L[8] + R[8], 2))))
        print (ciphertext)
        exit(1)
        writeImageFile (ciphertext, outputFile)
        return ciphertext
    else:
        ciphertext = ""
        for i in tqdm(range(len(text))):
            L[0] = make_bitseq(text[i])[:len(make_bitseq(text[i]))//2]
            R[0] = make_bitseq(text[i])[len(make_bitseq(text[i]))//2:]
            for j in range (1, 9):
                L[j] = R[j - 1]
                R[j] = XOR(L[j - 1], f(R[j - 1], j, key))
            ciphertext += (chr(int(L[8] + R[8],2)))
        writeTextFile (ciphertext, outputFile)
        return ciphertext
    

# decrypts a ciphertext
def decryptText (text, outputFile, key, mode):
    print ("\t\tDecrypting")
    if (mode):
        plaintext = bytearray()
    else:
        plaintext = ""
    L = [""] * (9)
    R = [""] * (9)

    if (mode):
        for i in tqdm(range(len(text))):
            bit8 = '{0:08b}'.format(text[i], 'b')
            L[8] = bit8[:len(bit8)//2]
            R[8] = bit8[len(bit8)//2:]
            for j in range (8, 0, -1):
                R[j - 1] = L[j]
                L[j - 1] = XOR(R[j], f(L[j], j, key))
            plaintext.append(ord(chr(int(L[0] + R[0], 2))))
        writeImageFile (plaintext, outputFile)
    else:
        for i in tqdm(range(len(text))):
            L[8] = make_bitseq(text[i])[:len(make_bitseq(text[i]))//2]
            R[8] = make_bitseq(text[i])[len(make_bitseq(text[i]))//2:]
            for j in range (8, 0, -1):
                R[j - 1] = L[j]
                L[j - 1] = XOR(R[j], f(L[j], j, key))
            plaintext += (chr(int(L[0] + R[0],2)))
        writeTextFile (plaintext, outputFile)
        
    return plaintext

# encrypts a plaintext
def encrypt (text, key):
    L = [""] * (9)
    R = [""] * (9)

    ciphertext = ""
    for i in tqdm(range(len(text))):
        bit8 = '{0:08b}'.format(text[i], 'b')
        L[0] = bit8[:len(bit8)//2]
        R[0] = bit8[len(bit8)//2:]
        for j in range (1, 9):
            L[j] = R[j - 1]
            R[j] = XOR(L[j - 1], f(R[j - 1], j, key))
        ciphertext += L[8] + R[8]

    return ciphertext


# decrypts a ciphertext
def decrypt (text, key):

    plaintext = []
    L = [""] * (9)
    R = [""] * (9)

    for i in tqdm(range(len(text))):
        bit8 = '{0:08b}'.format(text[i], 'b')
        L[8] = bit8[:len(bit8)//2]
        R[8] = bit8[len(bit8)//2:]
        for j in range (8, 0, -1):
            R[j - 1] = L[j]
            L[j - 1] = XOR(R[j], f(L[j], j, key))
        plaintext.append(ord(chr(int(L[0] + R[0], 2))))
        
    return plaintext


# the Feistal Cipher function
def f(b,ind,key):
    k = int (make_bitseq(key), 2)
    x = int (b, 2)
    r = pow((2 * ind * k), x) % 15
    return r

# XOR function
def XOR(a,b):
    b = '{0:04b}'.format(b)
    
    while (len(b) < 4):
        b = '0' + b
    while (len(a) < 4):
        a = '0' + a
    
    r = ""
    for i in range(len(b)):
        k = int (a[i], 2)
        p = int (b[i], 2)
        r += str(p ^ k)

    return r

# converts string to binary
def make_bitseq(s: str) -> str:
    return "".join(f"{ord(i):08b}" for i in s)

# binary to ascii characters
def bits2a(b):
    return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))

# writes into a file
def writeImageFile (text, file):
    f = open(file, "wb+")
    f.write(text)
    f.close()

# reads a file
def readImageFile (file):
    try:
        st = os.stat(file)
    except os.error:
        print ("File Not Found")
        sys.exit(5)
    f = open(file, "rb")
    txt = f.read()
    return txt

# reads a file
def readTextFile (file):
    try:
        st = os.stat(file)
    except os.error:
        print ("File Not Found")
        sys.exit(5)
    f = open(file, "r")
    txt = f.read()
    return txt

# writes into a file
def writeTextFile (text, file):
    f = open(file, "w")
    f.write(text)
    f.close()

# main function call
if __name__ == "__main__":
    main (sys.argv[1:])
