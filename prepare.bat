#Script to automate 

#Run autopep8
..\..\..\python\conda\Scripts\autopep8  .\ --recursive --in-place --pep8-passes 100 --verbose

#Run unit tests
..\..\..\python\conda\python unit_tests\run_unit_tests.py

#Generate documentation
#run pydoc

#Send to GitHub


