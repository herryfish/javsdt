import redis
import sys

def getConectionPool():
	pool = redis.ConnectionPool(host='192.168.1.251', port=6379, decode_responses=True)
	r = redis.Redis(connection_pool=pool)
	return r

def checkRedisKey(key):
	r = getConectionPool()
	ret = r.get(key)
	if None != ret:
		print(ret)
	return ret

def setRedisKeyValue(key, value):
	r = getConectionPool()
	r.set(key, value)

def printAll(mypattern):
	r = getConectionPool()
	pipe = r.pipeline()
	pipe_size = 100000
	
	len = 0
	key_list = []
	print(r.pipeline())
	keys = r.keys(pattern=mypattern)
	for key in keys:
		key_list.append(key)
		pipe.get(key)
		if len < pipe_size:
			len += 1
		else:
			for (k, v) in zip(key_list, pipe.execute()):
				print(k, v)
			len = 0
			key_list = []
	  
	for (k, v) in zip(key_list, pipe.execute()):
		print(k, v)

if __name__ == "__main__":
	if (len(sys.argv) == 1):
		printAll('*')
	elif ((len(sys.argv) == 2) and (sys.argv[1].find('*') >= 0)):
		printAll(sys.argv[1])
	else:
		for i in range(1,len(sys.argv)):
			checkRedisKey(sys.argv[i])