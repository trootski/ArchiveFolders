'''
Created on Apr 6, 2011

@author: troot
'''
import unittest
import os

from ArchiveFolders import ArchiveFolders

class ArchiveFoldersTest(unittest.TestCase):
	
	def setUp(self):
		#self.t = ArchiveFolders()
		pass
	
	def tearDown(self):
		#del self.t
		pass
	
	def test_get_slash_char(self):
		
		t = ArchiveFolders(xml_config_url="../../archive_config.xml")
		
		if os.name is "nt":
			self.assertEqual(t._get_slash_char(), "\\")
		else:
			self.assertEqual(t._get_slash_char(), "/")
		pass
	
if __name__ == "__main__":
	unittest.main()
	
