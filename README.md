# PMP Convert
## Description: <br/>
PMP Convert is a program that compresses PIL supported image formats into the .pmp format and decompresses .pmp files into bitmaps. PMP files are used in OPTWORKS games (18+) and any games using the same engine.

This program was made with the help of gocha's spioptw susie plugin as a reference for decompression (with some minor fixes): <br/>
https://github.com/gocha/spioptw

No generative AI was used in any step in the making of this program.

## Usage: <br/>
To use, put all images you would like to compress/decompress into the "convert" folder and run the run.bat file. The outputs will be in the "out" folder. <br/>

## Known Issues: <br/>
Sometimes has issues with PNG images that have fully transparent pixels.

## The PMP file format: <br/>
The PMP file format is a form of run length encoding. <br/>
It uses 24 bit color and decompresses from the bottom left to top right of the image, and does 2 scans for the top 4 and bottom 4 bits of each byte. <br/>
It consists of 7 sections: the header, and 1 flagmap and 1 value map for all 3 color channels. <br/>
Each section appears directly after each other in the same order they appear in the header.

### The Header: <br/>
The header is composed of 9 sections: <br/>
The first two bytes are the file magic and read "PM". <br/>
The next 4 bytes are the width of the image in little endian. <br/>
The next 4 bytes are the height of the image in little endian. <br/>
The next 4 bytes are the length of the blue flagmap in little endian. <br/>
The last 4 bytes are the length of the blue value map in little endian. <br/>
The next 4 bytes are the length of the green flagmap in little endian. <br/>
The last 4 bytes are the length of the green value map in little endian. <br/>
The next 4 bytes are the length of the red flagmap in little endian. <br/>
The last 4 bytes are the length of the red value map in little endian.

### Flagmaps: <br/>
Each flagmap is composed of a series of bytes read from the most to least significant bit, starting from the first byte after the header and going to the last byte before the corresponding value map. <br/>
Each bit corresponds to an instruction for decompressing the file. <br/>
A 1 means the next byte in the value map will be used for decompression.
A 0 means the current byte in the value map will be used for decompression.
Each flagmap always starts with a 1 as the most important bit in the first byte, so when decompressing its neccessary to have the value pointer be 1 byte before the first byte in the value map since it automatically moves over 1. <br/>
The first half of the image will be read as a first scan for the top 4 bits of each byte in the bitmap, then the second half of the image will be read as the second scan for the bottom 4 bits. </br>
It continues reading as normal between scans, only the pixel draw position gets reset.

### Value Maps: <br/>
Each value map consists of single bytes that are read differently depending on whether its being read during the first or second scan. <br/>
During decompression, each byte corresponds to the values of either the top or bottom 4 bits in the next two pixels on the bitmap. <br/>
During the first scan, the top 4 bits will be used as the top 4 bits of the first color drawn, and the bottom 4 bits will be used as the top 4 bits of the second color drawn. <br/>
After the first scan, it goes back to the start of the image and writes the bottom 4 bits of each color in the bitmap. <br/>
During the second scan, the top 4 bits will be used as the bottom 4 bits of the first color drawn, and the bottom 4 bits will be used as the bottom 4 bits of the second color drawn. <br/>

~Snow (she/her)