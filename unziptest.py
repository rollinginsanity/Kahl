#Just figuring out how to unzip files
import zipfile

zf = zipfile.ZipFile('comics/unprocessed/masseffect_foundation_vol1.cbz')
for file in zf.namelist():
    output = "comics/processed"
    zf.extract(file, output)
