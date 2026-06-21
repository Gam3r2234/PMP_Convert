import os
import numpy
from PIL import Image

def compressImage(inputFileName, pmpFileName):
        
    #get image info
    image = Image.open(inputFileName).convert("RGB")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    width = image.width
    height = image.height

    #get pixel data
    pixelList = list(image.getdata())
    pixelCount = len(pixelList)

    #compress px data
    Bflagmap = []
    BvalMap = [None]
    Gflagmap = []
    GvalMap = [None]
    Rflagmap = []
    RvalMap = [None]

    #high pass
    i=0
    while i < pixelCount:

        #look at next 2 pixels
        pixel1, pixel2 = pixelList[i], pixelList[i+1]

        #get top 4 bytes of each color value and append them together
        bval1, bval2 = pixel1[2], pixel2[2]
        bval = ((bval1 & 0xF0) + ((bval2 & 0xF0) >> 4)).to_bytes()
        gval1, gval2 = pixel1[1], pixel2[1]
        gval = ((gval1 & 0xF0) + ((gval2 & 0xF0) >> 4)).to_bytes()
        rval1, rval2 = pixel1[0], pixel2[0]
        rval = ((rval1 & 0xF0) + ((rval2 & 0xF0) >> 4)).to_bytes()
        
        #compare them to last item in valmap
        if bval == BvalMap[-1]:
            Bflagmap.append(0)
        else:
            Bflagmap.append(1)
            BvalMap.append(bval)
        if gval == GvalMap[-1]:
            Gflagmap.append(0)
        else:
            Gflagmap.append(1)
            GvalMap.append(gval)
        if rval == RvalMap[-1]:
            Rflagmap.append(0)
        else:
            Rflagmap.append(1)
            RvalMap.append(rval)

        i += 2

    #lowpass
    i=0
    while i < pixelCount:

        #look at next 2 pixels
        pixel1, pixel2 = pixelList[i], pixelList[i+1]

        #get top 4 bytes of each color value and append them together
        bval1, bval2 = pixel1[2], pixel2[2]
        bval = (((bval1 & 0x0F) << 4) + (bval2 & 0x0F)).to_bytes()
        gval1, gval2 = pixel1[1], pixel2[1]
        gval = (((gval1 & 0x0F) << 4) + (gval2 & 0x0F)).to_bytes()
        rval1, rval2 = pixel1[0], pixel2[0]
        rval = (((rval1 & 0x0F) << 4) + (rval2 & 0x0F)).to_bytes()

        #compare them to last item in valmap
        if bval == BvalMap[-1]:
            Bflagmap.append(0)
        else:
            Bflagmap.append(1)
            BvalMap.append(bval)
        if gval == GvalMap[-1]:
            Gflagmap.append(0)
        else:
            Gflagmap.append(1)
            GvalMap.append(gval)
        if rval == RvalMap[-1]:
            Rflagmap.append(0)
        else:
            Rflagmap.append(1)
            RvalMap.append(rval)

        i += 2

    #make flagmaps length a multiple of 8
    while len(Bflagmap) % 8 != 0:
        Bflagmap.append(0)
    while len(Gflagmap) % 8 != 0:
        Gflagmap.append(0)
    while len(Rflagmap) % 8 != 0:
        Rflagmap.append(0)

    #make actual flagmaps
    TrueBflagmap = []
    TrueGflagmap = []
    TrueRflagmap = []

    i = 0
    while i < len(Bflagmap):
        currentByte = []
        currentByte.extend(Bflagmap[i:i+8])
        currentNum = 0
        for bit in currentByte:
            currentNum = 2* currentNum + bit
        TrueBflagmap.append(currentNum.to_bytes())
        i+=8
    i = 0
    while i < len(Gflagmap):
        currentByte = []
        currentByte.extend(Gflagmap[i:i+8])
        currentNum = 0
        for bit in currentByte:
            currentNum = 2* currentNum + bit
        TrueGflagmap.append(currentNum.to_bytes())
        i+=8
    i = 0
    while i < len(Rflagmap):
        currentByte = []
        currentByte.extend(Rflagmap[i:i+8])
        currentNum = 0
        for bit in currentByte:
            currentNum = 2* currentNum + bit
        TrueRflagmap.append(currentNum.to_bytes())
        i+=8

    #get rid of the strings
    BvalMap.pop(0)
    GvalMap.pop(0)
    RvalMap.pop(0)

    mapList = [TrueBflagmap, BvalMap, TrueGflagmap, GvalMap, TrueRflagmap, RvalMap]
   
    #make pmp file
    pmpFileHeader = b"PM"
    pmpFileHeader += int(width).to_bytes(4, "little")
    pmpFileHeader += int(height).to_bytes(4,"little")
    pmpFileHeader += int(len(TrueBflagmap)).to_bytes(4, "little")
    pmpFileHeader += int(len(BvalMap)).to_bytes(4, "little")
    pmpFileHeader += int(len(TrueGflagmap)).to_bytes(4, "little")
    pmpFileHeader += int(len(GvalMap)).to_bytes(4, "little")
    pmpFileHeader += int(len(TrueRflagmap)).to_bytes(4, "little")
    pmpFileHeader += int(len(RvalMap)).to_bytes(4, "little")

    with open(pmpFileName, "wb") as pmpFile:
        pmpFile.write(pmpFileHeader)
        for map in mapList:
            for value in map:
                pmpFile.write(value)
        pmpFile.close()
    
    print(os.path.basename(inputFileName) + " converted to " + os.path.basename(pmpFileName))