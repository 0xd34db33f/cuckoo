'''
Copyright (c) 2015
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL RYAN KEYES OR HIS EMPLOYER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
 
'''
Special appreciation goes out to Spawn for his IPREP code. While all of this code is entirely new and of my own creation, I do acknowledge working with
him on it and he was the inspiration for it
'''

from lib.cuckoo.common.abstracts import Signature
import urllib2
import os.path as path
import time
import os
import re

BASE_URL = "https://punchplusplus.miscreantpunchers.net/feeds.php?feed=pcres.txt&apikey="
API_KEY = "PLACE_API_KEY_HERE"
PCRE_FILE = "pcre-punchplusplus"
REFRESH_TIME=120

class NetworkPunchPlusPlus(Signature):
	
	name = "network_punchplusplus"
	description = "URL(s) match PCRE in the Punch++ Database"
	severity = 2
	categories = ["network"]
	authors = ["0xd34db33f"]
	minimum = "1.2"

	def downloadUpdatedList(self):
		success = True
		try:
			httpResponse = urllib2.urlopen(BASE_URL+API_KEY)
			outputFile = open(PCRE_FILE,'w')
			outputFile.write(httpResponse.read())
			outputFile.close()
			httpResponse.close()
		except Exception,e:
			success = False
		return success

	def check_punchplusplus(self):
		with open(PCRE_FILE) as content_file:
			pcre_contents = content_file.readlines()
			for pcre in pcre_contents:
				if not pcre.startswith("#"):
					pcre_data = pcre.strip('\n').split('\t')
					if self.check_url(pattern=pcre_data[0], regex=True):
						self.add_match(None,"Regex",pcre_data[0]+" - "+pcre_data[1])

	def run(self):
		filePresent = True
		if not path.isfile(PCRE_FILE) or (time.time()-path.getmtime(PCRE_FILE))/60 > REFRESH_TIME:
			filePresent = self.downloadUpdatedList()
		
		if filePresent and "http" in self.results["network"]:
			if len(self.results["network"]["http"]) > 0:
				self.check_punchplusplus()
        	return filePresent & self.has_matches()
