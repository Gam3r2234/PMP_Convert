import os
import numpy

def decompressImage(pmpFileName, bmpFileName):
    with open(pmpFileName, "rb") as pmpFile:

        #read magic
        pmpfilemagic = pmpFile.read(2)

        if pmpfilemagic == b"PM":

            #read header
            width = int.from_bytes(pmpFile.read(4), "little")
            height =  int.from_bytes(pmpFile.read(4), "little")
            BflagmapSize =  int.from_bytes(pmpFile.read(4), "little")
            BvalmapSize = int.from_bytes(pmpFile.read(4), "little")
            GflagmapSize =  int.from_bytes(pmpFile.read(4), "little")
            GvalmapSize = int.from_bytes(pmpFile.read(4), "little")
            RflagmapSize =  int.from_bytes(pmpFile.read(4), "little")
            RvalmapSize = int.from_bytes(pmpFile.read(4), "little")
            pmpFileSize = os.path.getsize(pmpFileName)
            headersize = 34

            #get offsets
            BflagmapOfs = headersize
            BvalmapOfs = BflagmapOfs + BflagmapSize
            GflagmapOfs = BvalmapOfs + BvalmapSize 
            GvalmapOfs = GflagmapOfs + GflagmapSize 
            RflagmapOfs = GvalmapOfs + GvalmapSize 
            RvalmapOfs = RflagmapOfs + RflagmapSize
            #we have to read from 1 spot behind the valmap initiallly, since the first flag value is always 1
            BvalReadOfs = BvalmapOfs - 1 
            GvalReadOfs = GvalmapOfs - 1 
            RvalReadOfs = RvalmapOfs - 1 

            #get initial values from valmaps
            pmpFile.seek(BvalReadOfs)
            Bval = int.from_bytes(pmpFile.read(1))
            pmpFile.seek(GvalReadOfs)
            Gval = int.from_bytes(pmpFile.read(1))
            pmpFile.seek(RvalReadOfs)
            Rval = int.from_bytes(pmpFile.read(1))

            #get other useful variables n stuff
            scanSize = width * height / 16
            pixelColorList = []

            #high bit scan
            #define high bit masks
            Bval1 = Bval & 0xF0
            Bval2 = (Bval << 4) & 0xF0
            Gval1 = Gval & 0xF0
            Gval2 = (Gval << 4) & 0xF0
            Rval1 = Rval & 0xF0
            Rval2 = (Rval << 4) & 0xF0

            pixelFlagOfs = 0
            while pixelFlagOfs < scanSize:

                #each pixel flag is read one bit at a time
                #each color flag gives what to do for the top 4 bytes of the color
                pmpFile.seek(BflagmapOfs + pixelFlagOfs)
                Bflagbyte = int.from_bytes(pmpFile.read(1))
                pmpFile.seek(GflagmapOfs + pixelFlagOfs)
                Gflagbyte = int.from_bytes(pmpFile.read(1))
                pmpFile.seek(RflagmapOfs + pixelFlagOfs)
                Rflagbyte = int.from_bytes(pmpFile.read(1))
                
                #loop over every bit in the byte
                n=7
                while n >= 0:
                    Bflagbit = Bflagbyte & (1 << n) > 0
                    Gflagbit = Gflagbyte & (1 << n) > 0
                    Rflagbit = Rflagbyte & (1 << n) > 0

                    #if bit is 1, increase valReadOfs by 1
                    if Bflagbit:
                        BvalReadOfs += 1
                        pmpFile.seek(BvalReadOfs)
                        Bval = int.from_bytes(pmpFile.read(1))
                        Bval1 = Bval & 0xF0
                        Bval2 = (Bval << 4) & 0xF0
                    if Gflagbit:
                        GvalReadOfs += 1
                        pmpFile.seek(GvalReadOfs)
                        Gval = int.from_bytes(pmpFile.read(1))
                        Gval1 = Gval & 0xF0
                        Gval2 = (Gval << 4) & 0xF0
                    if Rflagbit:
                        RvalReadOfs += 1
                        pmpFile.seek(RvalReadOfs)
                        Rval = int.from_bytes(pmpFile.read(1))
                        Rval1 = Rval & 0xF0
                        Rval2 = (Rval << 4) & 0xF0

                    pixelColorList.append(Bval1)
                    pixelColorList.append(Gval1)
                    pixelColorList.append(Rval1)
                    pixelColorList.append(Bval2)
                    pixelColorList.append(Gval2)
                    pixelColorList.append(Rval2)
                    
                    n-=1

                pixelFlagOfs += 1

            #low bit scan
            #define low bit masks

            Bval1 = (Bval >> 4)
            Bval2 = Bval & 0x0F
            Gval1 = (Gval >> 4)
            Gval2 = Gval & 0x0F
            Rval1 = (Rval >> 4)
            Rval2 = Rval & 0x0F

            colOfs = 0
            while pixelFlagOfs < scanSize*2:

                #each pixel flag is read one bit at a time
                #each color flag gives what to do for the top 4 bytes of the color
                pmpFile.seek(BflagmapOfs + pixelFlagOfs)
                Bflagbyte = int.from_bytes(pmpFile.read(1))
                pmpFile.seek(GflagmapOfs + pixelFlagOfs)
                Gflagbyte = int.from_bytes(pmpFile.read(1))
                pmpFile.seek(RflagmapOfs + pixelFlagOfs)
                Rflagbyte = int.from_bytes(pmpFile.read(1))     
                
                #loop over every bit in the byte
                n=7
                while n >= 0:
                    Bflagbit = Bflagbyte & (1 << n) > 0
                    Gflagbit = Gflagbyte & (1 << n) > 0
                    Rflagbit = Rflagbyte & (1 << n) > 0

                    #if bit is 1, increase valmapOfs by 1
                    if Bflagbit:
                        BvalReadOfs += 1
                        pmpFile.seek(BvalReadOfs)
                        Bval = int.from_bytes(pmpFile.read(1))
                        Bval1 = (Bval >> 4)
                        Bval2 = Bval & 0x0F
                    if Gflagbit:
                        GvalReadOfs += 1
                        pmpFile.seek(GvalReadOfs)
                        Gval = int.from_bytes(pmpFile.read(1))
                        Gval1 = (Gval >> 4)
                        Gval2 = Gval & 0x0F
                    if Rflagbit:
                        RvalReadOfs += 1
                        pmpFile.seek(RvalReadOfs)
                        Rval = int.from_bytes(pmpFile.read(1))
                        Rval1 = (Rval >> 4)
                        Rval2 = Rval & 0x0F

                    pixelColorList[colOfs] += Bval1
                    pixelColorList[colOfs + 1] += Gval1
                    pixelColorList[colOfs + 2] += Rval1
                    pixelColorList[colOfs + 3] += Bval2
                    pixelColorList[colOfs + 4] += Gval2
                    pixelColorList[colOfs + 5] += Rval2
                    
                    n-=1
                    colOfs += 6

                pixelFlagOfs += 1

                        
            #make image the fucked up way
            #start of bitmap header
            bmpHeader = b"BM" #2 bytes
            bmpHeader += int(54+(width*height*3)).to_bytes(4, "little") #bmp file size
            bmpHeader += len([]).to_bytes(2) #doesnt matter
            bmpHeader += len([]).to_bytes(2) #doesnt matter
            bmpHeader += int(54).to_bytes(4, "little") #pixel start ofs
            #start of bitmapinfoheader
            bmpHeader += int(40).to_bytes(4, "little") #size of this header
            bmpHeader += width.to_bytes(4, "little") #width
            bmpHeader += height.to_bytes(4, "little") #height
            bmpHeader += int(1).to_bytes(2, "little") #color plane
            bmpHeader += int(24).to_bytes(2, "little") #bitsperpixel
            bmpHeader += int(0).to_bytes(4, "little") #no compression
            bmpHeader += int((width*height*3)).to_bytes(4, "little") #image size (default 0)
            bmpHeader += int(1).to_bytes(4, "little") #horiz res
            bmpHeader += int(1).to_bytes(4, "little") #vert res
            bmpHeader += int(0).to_bytes(4, "little") #colors in color palette (default 0)
            bmpHeader += int(0).to_bytes(4, "little") #important colors

            #write
            with open(bmpFileName, "wb") as outputFile:
                outputFile.write(bmpHeader)
                for val in pixelColorList:
                    outputFile.write(val.to_bytes())
                outputFile.close()

            print(os.path.basename(pmpFileName) + " converted to " + os.path.basename(bmpFileName))

        else:
            print("THIS IS NOT AN pmp FILE")