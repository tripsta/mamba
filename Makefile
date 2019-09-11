deps:
	pip install -r requirements.txt

rmpyc:
	find . -name "*.pyc" -exec rm -rf {} \;

test: rmpyc
	rm -rf _trial_temp
	PYTHONPATH=`pwd` trial -e mamba
