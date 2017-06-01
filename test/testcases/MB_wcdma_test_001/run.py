from pysys.constants import *
from pysys.basetest import BaseTest
from pysys.constants import Project 
import os
import platform
import commands

class PySysTest(BaseTest):
	
	def setup(self):
		errorfile = self.output+"/testscript.err"
		outfile = self.output+"/testscript.out"
		if os.path.isfile(errorfile):
			os.remove(errorfile)
		if os.path.isfile(outfile):
			os.remove(outfile)


	def execute(self):
		script = "%s/parsecfg.py" % ((self.input).split('testcases')[0]+'scripts')
	
		self.hprocess = self.startProcess(command=sys.executable,
						  arguments = [script,'wcdma'],
						  environs = os.environ,
						  workingDir = self.output,
						  stdout = "%s/testscript.out" % self.output,
						  stderr = "%s/testscript.err" % self.output,
						  state=FOREGROUND)
	
	def validate(self):
		if 'Linux' == platform.system():
			outfile = self.output+'/testscript.out' 
			errorfile = self.output+"/testscript.err"
			f = open(errorfile)
			lines = f.readlines()
			for line in lines:
				self.log.info(lines)
				self.assertTrue(1==2)
				return
			f = open(outfile)
			lines = f.readlines()
			for line in lines:
				if ''==line.strip():
					continue
				(status, output) = commands.getstatusoutput(line.strip())
				status = status>>8
				if status>2:
					self.log.info(line.strip())
					self.log.info('Status: '+str(status))
					self.log.info(output)
                                if status==2 and 'NRPE: ' in output:
                                        self.log.info(line.strip())
					self.log.info('Status: '+ str(status))
					self.log.info(output)
					self.assertTrue(1==2)
					continue
				self.assertTrue(status<3)
