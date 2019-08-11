# -*- coding: utf-8 -*-
# @Author: JimDreamHeart
# @Date:   2018-03-21 22:31:37
# @Last Modified by:   JimDreamHeart
# @Last Modified time: 2018-10-08 23:52:01

def initGlobal_GTo_Global():
	global _G;
	_G = {};

def isExist_G():
	global _G;
	try:
		if isinstance(_G, dict):
			return True;
	except Exception:
		pass;
	return False;

def isLockGlobal_G():
	global isLock_G;
	try:
		if isinstance(isLock_G, bool):
			return isLock_G;
	except Exception:
		pass;
	return False;

def setGlobalVarTo_Global(key, value, isCover = False):
	global _G;
	global isLock_G;
	if isLockGlobal_G():
		raise Exception("It is forbidden to set GlobalVar to _Global !");
	if isExist_G():
		if key not in _G or isCover == True:
			_G[key] = value;
		else:
			raise Exception("The global var of \"{0}\" is existed !".format(str(key)));
	else:
		raise Exception("The global var of _G is not init !");

def _GG(key):
	global _G;
	if isExist_G():
		try:
			return _G[key];
		except Exception:
			raise Exception("The global var of \"{0}\" is not exist !".format(str(key)));
	else:
		raise Exception("The global var of _G is not init !");

def lockGlobal_GTo_Global():
	global isLock_G;
	if isExist_G():
		isLock_G = True;

