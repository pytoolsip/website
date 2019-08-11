# -*- coding: utf-8 -*-
# @Author: JimDreamHeart
# @Date:   2018-04-19 14:22:56
# @Last Modified by:   JinZhang
# @Last Modified time: 2019-03-28 18:34:16

import os,sys,time;

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
	_loadLogger_(); # 加载日志类变量

# 加载全局日志类
def _loadLogger_():
	# Logger参数
	path = "log";
	name = "pytoolsip-website";
	curTimeStr = time.strftime("%Y_%m_%d", time.localtime());
	maxBytes = 102400000;
	backupCount = 10;
	# 保存Logger到全局变量中
	logger = Logger("Common", isLogFile = True, logFileName = os.path.join(CURRENT_PATH, path, name+("_%s.log"%curTimeStr)), maxBytes = maxBytes, backupCount = backupCount);
	_G.setGlobalVarTo_Global("Log", logger); # 设置日志类的全局变量
	return logger;
