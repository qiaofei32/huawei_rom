#!/usr/bin/env python
import os
import sys
import logging
from struct import unpack
from zipfile import ZipFile
from argparse import ArgumentParser

UNLOCK_CODE = b'HW7x27\xff\xff'
BLOCK_MAGIC_NUM = b'\x55\xAA\x5A\xA5'

logger = logging.getLogger("")

# fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
# datefmt = "%Y-%m-%d %H:%M:%S"

fmt = "%(asctime)-8s %(message)s"
datefmt = "%H:%M:%S"

formatter = logging.Formatter(fmt, datefmt)
logger_handler = logging.StreamHandler()
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)


def format_hex(s):
	try:
		ret = ''.join('{:02x}'.format(c) for c in s)
		return ret
	except:
		return ""


def get_update_app_from_zip(zip_path):
	with ZipFile(zip_path) as update_zip:
		return update_zip.open('UPDATE.APP')


class UpdateAppParser:
	def __init__(self, update_app):
		self.update_app = update_app
	
	def parse(self):
		null_padding = self.update_app.read(92)
		assert null_padding == b'\x00' * 92
		
		while True:
			logger.info("-----------------------------")
			self.update_app = self.parse_block()
			if self.update_app is None:
				break
	
	
	def parse_block(self):
		
		# HeaderId 4
		while True:
			magic_num = self.update_app.read(4)
			if magic_num == b'': # EOF
				logger.info("DONE...")
				return None
			if magic_num == BLOCK_MAGIC_NUM:
				logger.debug ("HeaderId 4")
				break
	
		# HeaderLength 4
		logger.debug("HeaderLength 4")
		header_len_bytes = self.update_app.read(4)
		header_len_int = unpack('<L', header_len_bytes)[0]
		logger.debug ("HeaderLength={}".format(header_len_int))
		
		# Unknown1 4
		logger.debug("Unknown1 4")
		unknown1 = self.update_app.read(4)
		assert unknown1 == b'\x01\x00\x00\x00', 'unknown1 not 0x01'
		
		# HardwareID 8
		logger.debug("HardwareID 8")
		unlock_code = self.update_app.read(8)
		# assert unlock_code == UNLOCK_CODE, 'unlock_code incorrect'
		
		# FileSequence 4
		logger.debug("FileSequence 4")
		module_id = self.update_app.read(4)
		
		# FileSize 4
		logger.debug("FileSize 4")
		data_len = self.update_app.read(4)
		data_len_int = unpack('<L', data_len)[0]
		logger.debug("FileSize={}".format(data_len_int))
		
		# FileDate 16
		logger.debug("FileDate 16")
		date = self.update_app.read(16)
		date_str = unpack('16s', date)[0].strip(b'\x00').decode('utf-8')
		
		# FileTime 16
		logger.debug("FileTime 16")
		time = self.update_app.read(16)
		time_str = unpack('16s', time)[0].strip(b'\x00').decode('utf-8')
		
		# FileType 16
		logger.debug("FileType 16")
		display_name = self.update_app.read(16)
		display_name_str = unpack('16s', display_name)[0].strip(b'\x00').decode('utf-8')
		logger.info(display_name_str)
		
		# Blank1 16
		logger.debug("Blank1 16")
		_ = self.update_app.read(16)
		
		# HeaderChecksum 2
		logger.debug("HeaderChecksum 2")
		unknown2 = self.update_app.read(2)
		
		# BlockSize 2
		logger.debug("BlockSize 2")
		block_size = self.update_app.read(2)
		block_size_int = unpack('<H', block_size)[0]
		
		# Blank2 2
		logger.debug("Blank2 2")
		block_size_hw = self.update_app.read(2)
		block_size_hw_int = unpack('<H', block_size_hw)[0]
		
		# Grab the checksum of the file
		remaining_header_len = header_len_int - (4 + 4 + 4 + 8 + 4 + 4 + 16 + 16 + 32 + 2 + 2 + 2)
		if remaining_header_len:
			buffer = self.update_app.read(remaining_header_len)
			checksum = format_hex(buffer)
		
		
		# Call the hooks
		self.on_header(
			unlock_code,
			module_id,
			date_str,
			time_str,
			display_name_str,
			block_size_int,
			block_size_hw_int,
		)
		
		self.on_data(self.update_app.read(data_len_int))
		
		# Ensure we finish on a 4 byte boundary alignment.
		alignment_padding = (4 - self.update_app.tell() % 4) % 4
		if alignment_padding:
			# logger.debug ('Seeking 0x{:08x} ahead'.format(alignment_padding))
			self.update_app.read(alignment_padding)
		
		return self.update_app
	
	def on_header(self,
				  unlock_code, module_id,
				  date_str,
				  time_str,
				  display_name_str,
				  block_size_int,
				  block_size_hw_int,
				  ):
		pass
	
	def on_data(self, data):
		pass


class DumpingParser(UpdateAppParser):
	def on_header(self,
				  unlock_code,
				  module_id,
				  date_str,
				  time_str,
				  display_name_str,
				  block_size_int,
				  block_size_hw_int,
				  ):
		self.last_module_id = module_id
		self.name = display_name_str.lower()
		
	def on_data(self, data):
		dir_name = 'data/huawei_update_app_files'
		if not os.path.isdir(dir_name):
			os.makedirs(dir_name)
			
		file_name = '{}/{}.IMG'.format(dir_name, self.name.upper())
		logger.debug("Write Data: {}".format(file_name))
		open(file_name, 'wb').write(data)


def parse_file(update_file_path):
	if update_file_path.endswith('.zip'):
		update_app = get_update_app_from_zip(update_file_path)
	elif update_file_path.endswith('.APP'):
		update_app = open(update_file_path, 'rb')
	else:
		raise 'Unrecognised file name.'
	
	parser = DumpingParser(update_app)
	parser.parse()

if __name__ == '__main__':
	argparser = ArgumentParser(description='Work with Huawei UPDATE.APP (and update.zip) files.')
	argparser.add_argument('-f', '--update_file', help='Should be an UPDATE.APP file, or an update.zip with an UPDATE.APP in it.')
	argparser.add_argument('-v', '--verbose', help='verbose')
	args = argparser.parse_args()
	
	update_file_path = args.update_file
	verbose = args.verbose
	
	if verbose:
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)
	
	parse_file(update_file_path)
	
	
