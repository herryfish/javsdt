import os,sys
import xml.etree.ElementTree as ET
from vid_cache import VidCache

def get_data(root, key, defualt = ''):
	data = root.find(key)
	if data != None:
		return data.text
	else:
		return defualt

def readNfo(file, cache):

	path = os.path.dirname(file)
	tree = ET.parse(file)
	root = tree.getroot()
	actors = []
	tags = []

	#for elem in root.iter():
	#	print (elem.tag, elem.attrib)

	title = get_data(root, 'title')
	premiered = get_data(root, 'premiered')
	jav_num = get_data(root, 'id')
	plot = get_data(root, 'plot')
	mpaa = get_data(root, 'mpaa')
	release = get_data(root, 'release')
	runtime = get_data(root, 'runtime')
	country = get_data(root, 'country')
	studio = get_data(root, 'studio')
	director = get_data(root, 'director')
	rate = get_data(root, 'rating', '0')

	for item in root.iterfind('actor'):
		actors.append(get_data(item, 'name'))
	actor = ','.join(actors)

	for item in root.iterfind('tag'):
		tags.append(item.text)
	tag = ','.join(tags)

	#print(jav_num, title, actor, plot, tag, mpaa, country, release, runtime, director, studio)
	#if (checkRedisKey(jav_num) == None):
	#	setRedisKeyValue(jav_num , title + '【' + ' '.join(actors) + '】('+ premiered + ')')
	#	insertintoDB(jav_num, title, actor, plot, tag, mpaa, country, release, runtime, director, studio, rate, path)
	cache.add(jav_num, title, actor, plot, tag, mpaa, country, release, runtime, director, studio, rate, path)
	#if not cache.contains(jav_num):
	#	insertintoDB(db, jav_num, title, actor, plot, tag, mpaa, country, release, runtime, director, studio, rate, path)
	#else:
	#	updateDB(db, jav_num, title, actor, plot, tag, mpaa, country, release, runtime, director, studio, rate, path)

def searchNfoFile(root_choose, cache = None):
	i = 1
	for root, dirs, files in os.walk(root_choose):
		if not files:
			continue
		for file_raw in files:
			if file_raw.endswith('.nfo'):
				readNfo(root + os.sep + file_raw, cache)
				print('*', end='', flush=True)
				i += 1
	print('\n' + str(i) + ' files finished.')


if __name__ == "__main__":
	
	try:

		cache = VidCache()
		searchNfoFile(sys.argv[1], db, cache)
		#readNfo(r'\\192.168.1.251\Data\SystemData\abp\【AIKA 天海つばさ】IPZ-713\IPZ-713 天海 VS AIKA 実録！キャバクラドキュメント 4Days キャバ嬢達の枕営業の実態を4日間盗撮.nfo')

	except:
		print(sys.exc_info())