# -*- coding: utf-8 -*-
# @Author: JimDreamHeart
# @Date:   2018-04-19 14:22:56
# @Last Modified by:   JinZhang
# @Last Modified time: 2019-03-28 18:34:16
import re,os,sys,time;

logLevel = "debug";

# 当前文件位置
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
# 添加搜索路径
if CURRENT_PATH not in sys.path:
	sys.path.append(CURRENT_PATH);
if os.path.join(CURRENT_PATH, "core") not in sys.path:
	sys.path.append(os.path.join(CURRENT_PATH, "core"));

# 加载全局变量
import _Global as _G;
from logCore.Logger import Logger;
from rsaCore import encodeStr, decodeStr, getPublicKey;
from ConsumerMgr import ConsumerMgr;

from website.settings import HOME_URL;

# 初始化全局变量
def _initGlobal_G_():
	_G.initGlobal_GTo_Global();

# 锁定全局变量
def _lockGlobal_G_():
	_G.lockGlobal_GTo_Global();

# 加载全局变量信息
def loadGlobalInfo():
	_initGlobal_G_(); # 初始化全局变量
	_loadGlobal_(); # 加载全局变量
	_lockGlobal_G_(); # 锁定全局变量

# 加载全局变量
def _loadGlobal_():
	_loadPath_(); # 加载全局路径
	_loadLogger_(); # 加载日志类变量
	_loadRsaDecode_(); # 加载rsa密钥解码方法
	_updateWsJSFile_(); # 更新websocket文件
	_loadConsumerMgr_(); # 加载websocket消费者管理类

# 加载全局路径
def _loadPath_():
	_G.setGlobalVarTo_Global("ProjectPath", CURRENT_PATH); # 设置工程路径的全局变量

# 加载全局日志类
def _loadLogger_():
	# Logger参数
	path = "log";
	name = "pytoolsip-website";
	curTimeStr = time.strftime("%Y_%m_%d", time.localtime());
	maxBytes = 102400000;
	backupCount = 10;
	# 保存Logger到全局变量中
	logger = Logger("Common", level = logLevel, isLogFile = True, logFileName = os.path.join(CURRENT_PATH, path, name+("_%s.log"%curTimeStr)), maxBytes = maxBytes, backupCount = backupCount);
	_G.setGlobalVarTo_Global("Log", logger); # 设置日志类的全局变量
	return logger;

# 加载rsa密钥解码方法
def _loadRsaDecode_():
	# 加载rsa密钥编解码方法
	_G.setGlobalVarTo_Global("EncodeStr", encodeStr);
	_G.setGlobalVarTo_Global("DecodeStr", decodeStr);
	# 更新main.js的公钥和首页地址
	publicKey = getPublicKey();
	publicKey = publicKey.replace("\n", "")
	mainJSFile, content = os.path.join(CURRENT_PATH, "assets", "static", "js", "main.js"), "";
	with open(mainJSFile, "r", encoding = "utf-8") as f:
		isPking = False;
		for line in f.readlines():
			# 更新HOME_URL
			if re.search("var HOME_URL.*=.*\".*\"", line):
				line = re.sub("\".*\";?", f"\"{HOME_URL}\";", line);
			# 更新PUBLIC_KEY
			if re.search("var PUBLIC_KEY.*\".*\"", line):
				line = re.sub("\".*\";?", f"\"{publicKey}\";", line);
			elif re.search("var PUBLIC_KEY.*\".*", line):
				line = re.sub("\".*;?", f"\"{publicKey}\";", line);
				isPking = True;
			else:
				if isPking:
					if re.search("\";?", line):
						isPking = False;
					continue;
			content += line;
	with open(mainJSFile, "w", encoding = "utf-8") as f:
		f.write(content);

# 更新websocket文件
def _updateWsJSFile_():
	# 更新首页地址
	wsJSFile, content = os.path.join(CURRENT_PATH, "assets", "static", "js", "ws.js"), "";
	with open(wsJSFile, "r", encoding = "utf-8") as f:
		isPking = False;
		for line in f.readlines():
			# 更新HOME_URL
			if re.search("var HOME_URL.*=.*\".*\"", line):
				if HOME_URL.find("https") >= 0:
					homeUrl = re.sub("https", "wss", HOME_URL);
				else:
					homeUrl = re.sub("http", "ws", HOME_URL);
				line = re.sub("\".*\";?", f"\"{homeUrl}\";", line);
			content += line;
	with open(wsJSFile, "w", encoding = "utf-8") as f:
		f.write(content);

# 加载websocket消费者管理类
def _loadConsumerMgr_():
	_G.setGlobalVarTo_Global("ConsumerMgr", ConsumerMgr());