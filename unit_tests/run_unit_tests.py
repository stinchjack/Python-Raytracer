import unittest, sys, os#, pkgutil, glob
""" Imports and runs all unit test is the unit_test directory, where 
the classes are children of unittest.TestCase and the file names 
the classes are in files name test_*.py
"""
sys.path.insert(0, ".\\")
sys.path.insert(0, ".\\unit_tests")

dirname = "unit_tests"

for name in os.listdir(dirname):
    if name.endswith(".py"):
        if name[:5]=="test_":

			#strip the extension
            module = name[:-3]
			# set the module name in the current global name space:

            globals()[module] = __import__(module)
				
for cls in unittest.TestCase.__subclasses__():
	if ("test_" in cls.__module__):
		
		exec("t = %s.%s "%(cls.__module__,cls.__name__))
		unittest.main()
	
