import os
from PIL import Image

from compressPMP import compressImage
from decompressPMP import decompressImage

extensionDict = Image.registered_extensions()
validExtensions = []
for key in extensionDict:
    validExtensions.append(key)
validExtensions = tuple(validExtensions)

for file in os.listdir("convert"):
    if file.lower().endswith(".pmp"):
        outname = os.path.splitext(os.path.basename(file))
        outname = "out\\" + outname[0] + ".bmp"
        decompressImage("convert\\" + file, outname)
    elif file.lower().endswith(validExtensions):
        outname = os.path.splitext(os.path.basename(file))
        outname = "out\\" + outname[0] + ".pmp"
        compressImage("convert\\" + file, outname)
    else:
        print("Invalid File Type")

input("Press Enter to close")