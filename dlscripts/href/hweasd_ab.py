import ftplib
import glob
import subprocess as sp
import csv
import numpy as np
import netCDF4 as nc4
import pygrib as pg
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import datetime
import scipy
import os
import sys
import matplotlib.colors as colors

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
from shutil import copyfile

datesub = str(sys.argv[1])
          
models = ["namnest","namnest_back","arw","arw_back","nmmb","nmmb_back","hrrr","hrrr_back"]
model_labels = ["Nam Nest","Nam Nest -12h", "ARW", "ARW -12h", "NMMB", "NMMB -12h", "HRRR", "HRRR -6h"]
masks = ["namnest","namnest","arw","arw","nmmb","nmmb","hrrr","hrrr"]
hweasd_fils = glob.glob('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/*hweasd*npy')

for fhour in range(0,31):

	print(fhour)
	start = datetime.datetime.now()
	plt.figure(figsize=(16,9))

	m = Basemap(projection='lcc',lat_0=5,lon_0=-100,llcrnrlon=-126,llcrnrlat=23,urcrnrlon=-63,urcrnrlat=50,resolution='l')
	shp_info = m.readshapefile('/gpfs_backup/stormtrack/jtradfor/ensemble_data/reference/st99_d00','states',drawbounds=False)

	ax = plt.gca()

	for nshape,seg in enumerate(m.states):
		poly = Polygon(seg,facecolor='white',edgecolor='white',zorder=1,linewidth=.5)
		poly2 = Polygon(seg,facecolor='none',edgecolor='black',zorder=3,linewidth=.5)
		ax.add_patch(poly)
		ax.add_patch(poly2)

	hweasds = []
	for k,model in enumerate(models):
		hweasd_fil = '/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/href/hweasd_%s.npy' % (model)
		hweasd_mask = '/gpfs_backup/stormtrack/jtradfor/ensemble_data/reference/%s_mask.npy' % (masks[k])
		temp_hweasd = np.load(hweasd_fil)[fhour]
		temp_mask = np.load(hweasd_mask)
		temp_hweasd[temp_mask] = np.nan
		hweasds.append(temp_hweasd/2.54) 

	hweasd_mean = np.mean(hweasds,axis=0)
	hweasds.append(hweasd_mean)

	hweasds_copy = np.copy(hweasds)    
	
	hweasds_sd = np.zeros_like(hweasds_copy[0])

	for i in range(0,len(hweasds_sd)):
		for j in range(0,len(hweasds_sd[0])):
			c = 0
			for k in range(0,3):
				for l in range(0,3):
					if i%3==k and j%3==l:
						hweasds_sd[i,j] = hweasds_copy[c][i,j]
					c+=1
	
	hweasds_sd[hweasds_sd>1000000] = np.nan	
	hweasds_sd[hweasds_sd>2] = 2.0
	hweasds_sd[hweasds_sd<=.02] = np.nan

	bounds = np.linspace(0,2,9)
	norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)

	im = m.imshow(hweasds_sd,zorder=2,norm=norm,aspect='equal',interpolation='none',vmin=0,vmax=2)
	cbar = plt.colorbar(im,fraction=0.023,ticks=[0,.25,.5,.75,1.0,1.25,1.5,1.75,2.0])
	cbar.ax.yaxis.set_tick_params(color='w')
	cbar.ax.set_yticklabels([0,.25,.5,.75,1.0,1.25,1.5,1.75,2.0],color='w')
	plt.box(False)
	sdfil = '/gpfs_backup/stormtrack/jtradfor/ensemble_data/wxenviz.github.io/uploads/outimages/href/%s%s00_hweasd_ab.png' % (datesub,str(fhour).zfill(2))
	plt.savefig(sdfil,facecolor='#101010',bbox_inches='tight',dpi=800)
	plt.close()
	print(datetime.datetime.now() - start)



