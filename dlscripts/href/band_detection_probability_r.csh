#!/bin/csh
#BSUB -o /gpfs_backup/stormtrack/jtradfor/ensemble_data/wxenviz.github.io/dlscripts/href/band_detection_probability_out
#BSUB -e /gpfs_backup/stormtrack/jtradfor/ensemble_data/wxenviz.github.io/dlscripts/href/band_detection_probability_err
#BSUB -n 4 
#BSUB -q mea716
#BSUB -R span[ptile=4]
#BSUB -W 12:15

source /usr/local/apps/mpich3/centos7/intelmpi2016.csh

unsetenv MPICH_NO_LOCAL

set datestr="193570000"
python /gpfs_backup/stormtrack/jtradfor/ensemble_data/wxenviz.github.io/dlscripts/href/band_detection_probability.py $datestr
