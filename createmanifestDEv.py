# Make manifest files from ASF sar downoads

# unzip>create medtadata>crate manifest>upload tifs/metadata/manfist to bucket
# todo: unzip 
# might be easiest to keep this in server/lunix


import glob, os
import json
import zipfile
from string import Template

# create base manifest
baseFolder =  r'C:\Users\johnj\Documents\SIG\15.goldmining\scripts\dummyData\S1B_IW_GRDH_1SDV_20200110T101421_20200110T101446_019753_025598_C902-PREDORB-10m-power-filt-rtc-gamma'
bucket = 'goldminehack'

def asfMetadata(baseFolder):
	baseFile = baseFolder.split('\\')[-1].split('_')
	baseMeta = ["mission","beanMode","productTypeRes","processingLvlClass","startDate","endDate","absOrbit","mdtID","uniqID"]
	a = dict(zip(baseMeta,baseFile))
	return json.dumps(a)


def prepTileSet(baseFolder):
	""" returns tifs in tileset template as list of stings """
	bands = glob.glob(baseFolder+'\\*.tif')
	tileSets = Template("""{"id": "$iD","sources":[{"uris": ["$img"]}]}""")
	bandsBase = Template(""" {"id":"$bandId", "tileset_id":"$tilesetId"} """)
	tList = []
	bList = []
	for i in bands:
		try:
			i = i.split('\\')[-1]
			img = 'gs://{}/{}'.format(bucket,i)
			iD = i.split('_')
			if iD[-1].split('.')[0] == 'map':
				iD = iD[-2].split('-')[1]
			else:
				iD= iD[-1].split('.')[0]
			tileSetsObj = tileSets.substitute(iD=iD,img=img)
			bandsObj = bandsBase.substitute(bandId=iD,tilesetId=iD)
			tList.append(tileSetsObj)
			bList.append(bandsObj)
			
		except:
			print("Image format doesn't match expected pattern")
	return tList, bList


def makeManifest(baseFolder):
	manifestBase = \
	""" {"name": "projects/earthengine-legacy/assets/$assPath",
		"tilesets": [$tilesets],
		"bands": [$bands],
	  	"properties": $properties
	  	}"""
	
	
	properties = asfMetadata(baseFolder)
	tiles, bands = prepTileSet(baseFolder)
	tiles = ','.join(tiles)
	bands = ','.join(bands)
	outname = 'upload/'+baseFolder.split('\\')[-1]
	os.makedirs(os.path.dirname(outname), exist_ok=True)
	fullManifest = Template(manifestBase).substitute(assPath='users/TEST/manifestUpload',tilesets=tiles,bands=bands,properties=properties)
	with open(outname+'.json','a') as something:
		something.write(fullManifest)


# makeManifest(baseFolder)
if __name__ == "__main__":
	zipList = glob.glob('*.zip')
	print(zipList)
	print(os.getcwd())
	for i in zipList:
		with zipfile.ZipFile(i,"r") as zip_ref:
			zip_ref.extractall('tmp')
		targetdir = i[:-4]
		er = os.getcwd()+'\\tmp\\'+targetdir
		makeManifest(er)
		for j in glob.glob(er+"\\*.tif"):
			os.rename(j,"{}{}{}".format(os.getcwd(),'\\upload\\',j.split('\\')[-1]))
# 	# list all tifs