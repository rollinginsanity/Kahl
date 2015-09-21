import zipfile

def add(x, y):
	return x + y

def extractcomic(comicfile):
	zf = zipfile.ZipFile(comicfile)
	for file in zf.namelist():
		output = "comics/processed/me"
		zf.extract(file, output)
