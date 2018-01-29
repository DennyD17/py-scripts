#!/bin/sh

source /home/infaprm2/.profile
cd /etldata/scripts/workflows_check
python workflows_check.py 
touch start.flag

