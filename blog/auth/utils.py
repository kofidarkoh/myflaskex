from hashlib import sha256,md5,sha1
from random import random

meth = ["POST",'GET']

class Relationship_status:
	pending = 0
	accept = 1
	ignore = 2
	cancel = 3
	delete = 4


def GenHexDigest(salt , raw_password , algorithm_type = md5):
	"generete secure hash hexdigest algorithm_type md5 , sha256, sha1"
	data = str(salt) + str(raw_password)
	return algorithm_type(data.encode()).hexdigest()

def GenHashPassword(raw_password):
	'generate secure hash for user password, default algorithm_type sha256 and hexdigest with md5'
	salt = GenHexDigest(str(random()), str(random()))[:11]
	hsh = GenHexDigest(salt,raw_password,algorithm_type=md5)
	return "%s$[ENCRYPTED]$%s" % (salt,hsh)

def CheckPassword(hash_password, raw_password):
	salt,hsh = hash_password.split("$[ENCRYPTED]$",1)
	return GenHexDigest(salt,raw_password) == hsh
