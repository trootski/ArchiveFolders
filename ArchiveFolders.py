'''
Created on Apr 4, 2011

This script is designed to take all the files from one directory and move 
them to another date stamped folder. This reduces the amount of clutter 
on certain key folders which have a high amount of files created in them

@author: troot
'''

import os
from datetime import date
import re
import urllib
from xml.dom import minidom, Node
import shutil

class ArchiveFolders(): 
	
	def __init__(self, **kwargs):
		
		self.properties = kwargs
		
		self.properties['slash_char'] = self._get_slash_char()
		
		if self.xml_config_url is None:
			self.properties['xml_config_url'] = "../archive_config.xml"
		
	'''
		Run the archiving process
	'''
	def run(self):
		
		try:
			self.properties['config_dom'] = minidom.parse(urllib.urlopen(self.xml_config_url))
		except IOError:
			print "Couldn't find the configuration file. Please check the value and try again."
			exit()
		
		for ark in self._next_ark_config():
			
			try:
				self.properties['conf'] = self._process_ark_config(ark)
			except ValueError:
				print "There is an error in the xml config. Please check the file and try again"
			
			self._create_src_folders(self.conf.src_dir)
			
			self.conf.dest_dir = self._create_archive_folders(self.conf.dest_dir)
			
			self._execute_archiving(self.conf.src_dir, self.conf.dest_dir, self.slash_char)
	
	
	'''
		Loop through the src_dir and move each of its files/folders to the dest_dir (ignore hidden files)
	'''
	def _execute_archiving(self, src_dir, dest_dir, slash_char):
		
		srcFolderContents = os.listdir(src_dir)
		startDotREGEX = re.compile("^\.")
		
		for file in srcFolderContents:
			if not startDotREGEX.match(file) and not file in self.conf.ignore:
				print "%s%s%s" % (dest_dir, slash_char, file)
				shutil.move(
					"%s%s%s" % (src_dir, slash_char, file), 
					"%s%s%s" % (dest_dir, slash_char, file)
				)
	
	'''
		Check the src_dir exists. If it doesn't, create it
	'''
	def _create_src_folders(self, src_dir):
		try:
			
			if not os.path.exists(src_dir):
				os.makedirs(src_dir)
			
		except OSError as oe:
			print "Error creating the source folder. Please ensure you have permission to write the folder below." % oe
			exit()

	'''
		Create the dest_dir folder into which the files will be moved
	'''
	def _create_archive_folders(self, dest_dir):
		
		try:
			
			if not os.path.exists(dest_dir):
				raise OSError
			
			month_date_stub = date.today().strftime("%Y_%m")
			day_date_stub = date.today().strftime("%Y_%m_%d")
			lst_dest_dir = [month_date_stub, day_date_stub]
			
			dest_dir = "%s%s%s" % (dest_dir, self.slash_char, self.slash_char.join(i for i in lst_dest_dir))
			
			if not os.path.exists(dest_dir):
				os.makedirs(dest_dir)
			
			return dest_dir
			
		except OSError as oe:
			print "Error creating the destination folder. Please ensure you have permission to the folder below.\n%s" % oe
			exit()
	
	'''
		Read in the xml config (archive_config.xml) and save the settings
	'''
	def _next_ark_config(self):
		for node in self.config_dom.getElementsByTagName("ark"):
			yield node
		return
	
	'''
		Take an ark node and loop through the info inside
	'''
	def _process_ark_config(self, ark):
		
		ark_config = ArkConfig()
		self._remove_whitespace_nodes(ark)
		for node in ark.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				if node.nodeName.lower() == "src_config":
					for src_node in node.childNodes:
						if src_node.nodeName.lower() == "src_dir":
							ark_config.set_property('src_dir', self._get_node_text(src_node.childNodes))
						elif src_node.nodeName.lower() == "ignore":
							ark_config.ignore.append(self._get_node_text(src_node.childNodes))
				if node.nodeName.lower() == "dest_dir":
					ark_config.set_property('dest_dir', self._get_node_text(node.childNodes))
		
		return ark_config
	
	'''
		Given a particular node, get its text value
	'''
	def _get_node_text(self, node):
		retVal = ""
		for child in node:
			if child.nodeType == Node.TEXT_NODE:
				retVal = retVal + child.data
			elif child.nodeType == Node.CDATA_SECTION_NODE:
				retVal = retVal + child.data
			elif child.hasChildNodes():
				retVal = retVal + self._get_node_text(child.childNodes)
		return retVal

	'''
		Take white spaces out of the xml structure (they make traversing more difficult)
	'''
	def _remove_whitespace_nodes(self, node, unlink=False):
		remove_list = []
		for child in node.childNodes:
			if child.nodeType == Node.TEXT_NODE and not child.data.strip():
				remove_list.append(child)
			elif child.hasChildNodes():
				self._remove_whitespace_nodes(child, unlink)
		for node in remove_list:
			node.parentNode.removeChild(node)
			if unlink:
				node.unlink()
		
	'''
		Set what the folder delimeter should be
	'''
	def _get_slash_char(self):
		if os.name == "nt":
			return "\\"
		else:
			return "/"
	
	@property
	def slash_char(self): return self.properties.get('slash_char', None)

	@property
	def conf(self): return self.properties.get('conf', None)
	
	@property
	def xml_config_url(self): return self.properties.get('xml_config_url', None)
	
	@property
	def config_dom(self): return self.properties.get('config_dom', None)
	
class ArkConfig():
	
	def __init__(self, **kwargs):
		self.properties = kwargs
		self.properties['ignore'] = []
	
	def __repr__(self):
		return "ArkConfig (src_dir: %s, dest_dir: %s, ignore: %s" % (self.src_dir, self.dest_dir, self.ignore)
	
	def set_property(self, prop, val):
		self.properties[prop] = val
	
	@property
	def src_dir(self): return self.properties.get('src_dir', None)
	
	@property
	def dest_dir(self): return self.properties.get('dest_dir', None)
	@dest_dir.setter
	def dest_dir(self, val): self.properties['dest_dir'] = val
	@dest_dir.deleter
	def dest_dir(self): del self.properties['dest_dir']
	
	@property
	def ignore(self): return self.properties.get('ignore', None)
	
if __name__=="__main__":
	bf = ArchiveFolders()
	bf.run()


