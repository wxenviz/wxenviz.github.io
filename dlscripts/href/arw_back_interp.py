import ftplib
import glob
import subprocess as sp
import csv
import numpy as np
import netCDF4 as nc4
import pygrib as pg
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import scipy
import os
import sys
import re
import time
import subprocess as sp
import pickle

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
from shutil import copyfile
from datetime import datetime,timedelta

datesub = str(sys.argv[1])

Xrange = np.arange(-126,-63,0.025)
Yrange = np.arange(23,50,0.025)
[destmeshX,destmeshY] = np.meshgrid(Xrange,Yrange)
destpairs = np.zeros([destmeshX.shape[0]*destmeshX.shape[1],2])
destpairs[:,0] = destmeshX.flatten()
destpairs[:,1] = destmeshY.flatten()

m = Basemap(projection='lcc',lat_0=5,lon_0=-100,llcrnrlon=-126,llcrnrlat=23,urcrnrlon=-63,urcrnrlat=50,resolution='l')

X,Y = m(destmeshX,destmeshY)
nx = int((m.xmax-m.xmin)/3000.)+1; ny = int((m.ymax-m.ymin)/3000.)+1
crefs = []
brefs = []
apcps = []
aweasds = []
hpcps = []
hweasds = []
temps = []

for fhour in range(0,31):
	print(fhour)
	fil = '/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/%s%s00_arw_back.grib2' % (datesub,str(fhour).zfill(2))
	backfil = fil[:69] + str(fhour-1).zfill(2) + fil[71:]
	grbs = pg.open(fil)
	
	lat,lon = grbs[1].latlons()


	if fhour==0:
		apcp = np.zeros((1377,2145))
		aweasd = np.zeros((1377,2145))
		hpcp = np.zeros((1377,2145))
		hweasd = np.zeros((1377,2145))
		cref = np.zeros((1377,2145))
		bref = np.zeros((1377,2145))
		temperature = np.zeros((1377,2145))
		for grb in grbs:
			if 'Total Precipitation' in str(grb) and 'fcst time 0' in str(grb):
				apcpstart = grb.values[:]
			elif 'Water equivalent' in str(grb) and 'fcst time 0' in str(grb):
				aweasdstart = grb.values[:]
	else:
		grbsback = pg.open(backfil)
		for grb in grbs:
			if 'Total Precipitation' in str(grb) and 'fcst time 0' in str(grb):
				tempapcp = grb.values[:]
				apcp = tempapcp - apcpstart
			elif 'Water equivalent' in str(grb) and 'fcst time 0' in str(grb):
				tempaweasd = grb.values[:]
				aweasd = tempaweasd - aweasdstart
			elif 'level 1000' in str(grb):
				bref = grb.values[:]
			elif 'Maximum/Composite' in str(grb):
				cref = grb.values[:]
			elif 'temperature' in str(grb):
				temperature = grb.values[:]

		for grbback in grbsback:
			if 'Total Precipitation' in str(grbback) and 'fcst time 0' in str(grbback):
				tempapcpback = grbback.values[:]
				apcpback = tempapcpback - apcpstart
			elif 'Water equivalent' in str(grbback) and 'fcst time 0' in str(grbback):
				tempaweasdback = grbback.values[:]
				aweasdback = tempaweasdback - aweasdstart
			
		hpcp = apcp - apcpback
		hweasd = aweasd - aweasdback

	with open('/gpfs_backup/stormtrack/jtradfor/ensemble_data/reference/arw.tri', 'rb') as arw_tri:
		tri_arw = pickle.load(arw_tri)
	arw_tri.close()

	cref_flatten = cref.flatten()
	interpolator = LinearNDInterpolator(tri_arw,cref_flatten)
	temp = interpolator(destmeshX,destmeshY)
	cref_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	bref_flatten = bref.flatten()
	interpolator = LinearNDInterpolator(tri_arw,bref_flatten)
	temp = interpolator(destmeshX,destmeshY)
	bref_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	apcp_flatten = apcp.flatten()
	interpolator = LinearNDInterpolator(tri_arw,apcp_flatten)
	temp = interpolator(destmeshX,destmeshY)
	apcp_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	hpcp_flatten = hpcp.flatten()
	interpolator = LinearNDInterpolator(tri_arw,hpcp_flatten)
	temp = interpolator(destmeshX,destmeshY)
	hpcp_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	aweasd_flatten = aweasd.flatten()
	interpolator = LinearNDInterpolator(tri_arw,aweasd_flatten)
	temp = interpolator(destmeshX,destmeshY)
	aweasd_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	hweasd_flatten = hweasd.flatten()
	interpolator = LinearNDInterpolator(tri_arw,hweasd_flatten)
	temp = interpolator(destmeshX,destmeshY)
	hweasd_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	temperature_flatten = temperature.flatten()
	interpolator = LinearNDInterpolator(tri_arw,temperature_flatten)
	temp = interpolator(destmeshX,destmeshY)
	temperature_interp = m.transform_scalar(temp,Xrange,Yrange,nx,ny,masked=True)

	crefs.append(cref_interp.data)
	brefs.append(bref_interp.data)
	apcps.append(apcp_interp.data)
	aweasds.append(aweasd_interp.data)
	hpcps.append(hpcp_interp.data)
	hweasds.append(hweasd_interp.data)
	temps.append(temperature_interp.data)

np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/cref_arw_back.npy',crefs)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/bref_arw_back.npy',brefs)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/apcp_arw_back.npy',apcps)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/aweasd_arw_back.npy',aweasds)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/hpcp_arw_back.npy',hpcps)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/hweasd_arw_back.npy',hweasds)
np.save('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/temp_arw_back.npy',temps)
