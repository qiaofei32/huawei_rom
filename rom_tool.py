# -*- coding: utf-8 -*-
import os
import sys
import time
import thread
import subprocess
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtCore, QtGui
import parse_huawei_update_app

os.environ["CYGWIN"] = "nodosfilewarning"

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(519, 352)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.pushButton_huawei = QtGui.QPushButton(self.centralwidget)
		self.pushButton_huawei.setGeometry(QtCore.QRect(10, 10, 111, 41))
		self.pushButton_huawei.setObjectName(_fromUtf8("pushButton_huawei"))
		self.pushButton_parse_img = QtGui.QPushButton(self.centralwidget)
		self.pushButton_parse_img.setGeometry(QtCore.QRect(140, 10, 111, 41))
		self.pushButton_parse_img.setObjectName(_fromUtf8("pushButton_parse_img"))
		self.pushButton_parse_dat = QtGui.QPushButton(self.centralwidget)
		self.pushButton_parse_dat.setGeometry(QtCore.QRect(270, 10, 111, 41))
		self.pushButton_parse_dat.setObjectName(_fromUtf8("pushButton_parse_dat"))
		self.pushButton_img2dat = QtGui.QPushButton(self.centralwidget)
		self.pushButton_img2dat.setGeometry(QtCore.QRect(400, 10, 111, 41))
		self.pushButton_img2dat.setObjectName(_fromUtf8("pushButton_img2dat"))
		self.pushButton_pack2dat = QtGui.QPushButton(self.centralwidget)
		self.pushButton_pack2dat.setGeometry(QtCore.QRect(270, 70, 111, 41))
		self.pushButton_pack2dat.setObjectName(_fromUtf8("pushButton_pack2dat"))
		self.pushButton_pack2img = QtGui.QPushButton(self.centralwidget)
		self.pushButton_pack2img.setGeometry(QtCore.QRect(140, 70, 111, 41))
		self.pushButton_pack2img.setObjectName(_fromUtf8("pushButton_pack2img"))
		self.pushButton_dat2img = QtGui.QPushButton(self.centralwidget)
		self.pushButton_dat2img.setGeometry(QtCore.QRect(400, 70, 111, 41))
		self.pushButton_dat2img.setObjectName(_fromUtf8("pushButton_dat2img"))
		self.pushButton_unzip = QtGui.QPushButton(self.centralwidget)
		self.pushButton_unzip.setGeometry(QtCore.QRect(10, 70, 111, 41))
		self.pushButton_unzip.setObjectName(_fromUtf8("pushButton_unzip"))
		self.info_box = QtGui.QTextBrowser(self.centralwidget)
		self.info_box.setGeometry(QtCore.QRect(10, 120, 501, 221))
		self.info_box.setObjectName(_fromUtf8("info_box"))
		MainWindow.setCentralWidget(self.centralwidget)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(_translate("MainWindow", "ROM分析工具", None))
		self.pushButton_huawei.setText(_translate("MainWindow", "华为APP包解析", None))
		self.pushButton_parse_img.setText(_translate("MainWindow", "IMG文件解析", None))
		self.pushButton_parse_dat.setText(_translate("MainWindow", "Dat文件解析", None))
		self.pushButton_img2dat.setText(_translate("MainWindow", "IMG->Dat", None))
		self.pushButton_pack2dat.setText(_translate("MainWindow", "文件夹打包为Dat", None))
		self.pushButton_pack2img.setText(_translate("MainWindow", "文件夹打包为IMG", None))
		self.pushButton_dat2img.setText(_translate("MainWindow", "Dat->IMG", None))
		self.pushButton_unzip.setText(_translate("MainWindow", "ZIP包解压", None))
		self.info_box.setHtml("")
		self.pushButton_huawei.clicked.connect(self.huawei_app_parse)
		self.pushButton_parse_img.clicked.connect(self.parse_img)
		self.pushButton_parse_dat.clicked.connect(self.parse_dat)
		self.pushButton_unzip.clicked.connect(self.unzip)
		self.pushButton_pack2img.clicked.connect(self.pack2img)
		
		self.pushButton_img2dat.clicked.connect(self.todo)
		self.pushButton_dat2img.clicked.connect(self.todo)
		self.pushButton_pack2dat.clicked.connect(self.todo)
		
	def todo(self):
		msg_box = QMessageBox.information(None, u"说明", u"该项功能未实现!", QMessageBox.Yes)
	
	def do_cmd(self, *args):
		p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		stdout, stderr = p.communicate()
		print stdout, stderr
		
		self.CMD_DONE = True
		self.stdout = stdout
		self.stderr = stderr
		
	def huawei_app_parse(self):
		print u"解析华为APP升级包..."
		self.info_box.append(u"开始解析华为APP升级包...")
		
		file_dialog = QtGui.QFileDialog()
		file_path = file_dialog.getOpenFileNameAndFilter(caption=QString(u"华为APP包路径"), filter="*.APP")[0]
		file_path = unicode(file_path) # .encode("utf-8")
		print file_path
		file_path = file_path.encode("gbk")
		
		# self.CMD_DONE = False
		# args = ("perl",  "split_updata.pl", file_path)
		# thread.start_new_thread(self.do_cmd, args)
		# while not self.CMD_DONE:
		# 	time.sleep(0.5)
		
		parse_huawei_update_app.parse_file(file_path)
			
		self.info_box.append(u"完成解析华为APP升级包...")
	
	def is_img_or_dat(self, file_path):
		self.CMD_DONE = False
		args = ("bin/file.exe", file_path)
		thread.start_new_thread(self.do_cmd, args)
		while not self.CMD_DONE:
			time.sleep(0.5)
		
		if "Android sparse image" in self.stdout:
			print "Android sparse image"
			return "simg"
		
		if "ext4 filesystem data" in self.stdout:
			print "ext4 filesystem data"
			return "raw"
		
		return "err"
	
	def parse_img(self):
		print u"解析IMG文件..."
		self.info_box.append(u"开始解析IMG文件...")
		
		file_dialog = QtGui.QFileDialog()
		file_path = file_dialog.getOpenFileNameAndFilter(caption=QString(u"IMG文件路径"), filter="*.IMG *.DAT")[0]
		file_path = unicode(file_path) # .encode("utf-8")
		print file_path
		file_path = file_path.encode("gbk")
		
		file_type = self.is_img_or_dat(file_path)
		
		if file_type == "raw":
			# unpack-ext4fs image outdir
			self.info_box.append(u"文件为：raw ext4 filesystem")
			
			for i in range(1, 100):
				outdir = "data/parse_img_{}".format(i)
				if not os.path.isdir(outdir):
					break
				
			args = ("bin/unpack_ext4fs.exe",  file_path, outdir)
			self.CMD_DONE = False
			thread.start_new_thread(self.do_cmd, args)
			
			while not self.CMD_DONE:
				time.sleep(0.5)

			self.info_box.append(u"完成解析，存入目录{}...".format(outdir))
			
		elif file_type == "simg":
			# simg2img <sparse_image_file_in> <raw_image_file_out>
			self.info_box.append(u"文件为：Android sparse image")
			
			file_path_new = file_path.replace(".img", ".dat")
			file_path_new = file_path_new.replace(".IMG", ".dat")
			
			args = ("bin/simg2img.exe",  file_path, file_path_new)
			self.CMD_DONE = False
			thread.start_new_thread(self.do_cmd, args)
			
			while not self.CMD_DONE:
				time.sleep(0.5)
				
			self.info_box.append(u"转换：{} ---> {}".format(file_path, file_path_new))
			
			for i in range(1, 100):
				outdir = "data/parse_img_{}".format(i)
				if not os.path.isdir(outdir):
					break
			
			args = ("bin/unpack_ext4fs.exe", file_path_new, outdir)
			self.CMD_DONE = False
			thread.start_new_thread(self.do_cmd, args)
			
			while not self.CMD_DONE:
				time.sleep(0.5)
			
			self.info_box.append(u"完成解析，存入目录{}...".format(outdir))
		
	def parse_dat(self):
		"""
		Usage: sdat2img.py <transfer_list> <system_new_file> [system_img]
			<transfer_list>: transfer list file
			<system_new_file>: system new dat file
			[system_img]: output system image
		"""
		print u"解析DAT文件..."
		self.info_box.append(u"开始解析DAT文件...")
		
		file_dialog = QtGui.QFileDialog()
		ret = file_dialog.getOpenFileNames(caption=QString(u"同时选择system.new.dat和system.transfer.list文件"), filter="*.DAT *.LIST")
		# print list(ret)
		
		transfer_file = ""
		dat_file = ""
		
		for i in list(ret):
			i = unicode(i)
			if i.lower().endswith(".list"):
				transfer_file = i
				self.info_box.append(u"transfer file: {}".format(transfer_file))
				transfer_file = transfer_file.encode("gbk")
				
			elif i.lower().endswith(".dat"):
				dat_file = i
				self.info_box.append(u"dat file: {}".format(dat_file))
				dat_file = dat_file.encode("gbk")
		
		if transfer_file and dat_file:
			output_img = "data/parse_dat/system.img"
			args = ("bin/sdat2img.exe", transfer_file, dat_file, output_img)
			self.CMD_DONE = False
			thread.start_new_thread(self.do_cmd, args)
			
			while not self.CMD_DONE:
				time.sleep(0.5)
			
	def unzip(self):
		file_dialog = QtGui.QFileDialog()
		file_path = file_dialog.getOpenFileNameAndFilter(caption=QString(u"选择zip文件"), filter="*.zip")[0]
		file_path = unicode(file_path) # .encode("utf-8")
		print file_path
		file_path = file_path.encode("gbk")

		file_dialog = QtGui.QFileDialog()
		dir_path = file_dialog.getExistingDirectory(caption=QString(u"解压到目录"))
		dir_path = unicode(dir_path) # .encode("utf-8")
		print dir_path.replace("\\", "/")
		dir_path = dir_path.encode("gbk")
		
		if file_path and dir_path:
			args = ("bin/unzip.exe", file_path, "-d", dir_path)
			self.CMD_DONE = False
			thread.start_new_thread(self.do_cmd, args)
			
			while not self.CMD_DONE:
				time.sleep(0.5)
			
			self.info_box.append(u"解压缩zip完成...")
	
	def pack2img(self):
		file_dialog = QtGui.QFileDialog()
		dir_path = file_dialog.getExistingDirectory(caption=QString(u"打包目录"))
		dir_path = unicode(dir_path)  # .encode("utf-8")
		print dir_path.replace("\\", "/")
		dir_path = dir_path.encode("gbk")
		if not dir_path:
			return False
		
		file_dialog = QtGui.QFileDialog()
		output_dir_path = file_dialog.getExistingDirectory(caption=QString(u"存到目录"))
		output_dir_path = unicode(output_dir_path)  # .encode("utf-8")
		print output_dir_path.replace("\\", "/")
		output_dir_path = output_dir_path.encode("gbk")
		if not output_dir_path:
			return False
			
		"""
		make_ext4fs.exe -a system -s -l 1984M new.img dir_name"
		"""
		
		args = ("bin/make_ext4fs.exe", "-a", "system", "-s", "-l", "1984M", os.path.join(output_dir_path, "new.img"), dir_path)
		self.CMD_DONE = False
		thread.start_new_thread(self.do_cmd, args)
		
		while not self.CMD_DONE:
			time.sleep(0.5)
		
		self.info_box.append(u"打包完成...")
	
	

class ROM_TOOL(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = ROM_TOOL()
	win.show()
	sys.exit(app.exec_())