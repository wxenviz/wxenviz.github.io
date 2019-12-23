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

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
from shutil import copyfile

forecasthoursub = str(sys.argv[1])

plt.figure(figsize=(16,9))

m = Basemap(projection='lcc',lat_0=5,lon_0=-100,llcrnrlon=-126,llcrnrlat=23,urcrnrlon=-63,urcrnrlat=50,resolution='h')
shp_info = m.readshapefile('/gpfs_backup/stormtrack/jtradfor/ensemble_data/reference/st99_d00','states',drawbounds=False)

ax = plt.gca()

for nshape,seg in enumerate(m.states):
	poly = Polygon(seg,facecolor='white',edgecolor='white',zorder=1,linewidth=1)
	poly2 = Polygon(seg,facecolor='none',edgecolor='black',zorder=3,linewidth=1)
	ax.add_patch(poly)
	ax.add_patch(poly2)

snowtotals = np.load('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/sref/%s_asnow.npy' % (forecasthoursub))
forecasthoursubback = forecasthoursub[:9] + str(int(forecasthoursub[9:11]) - 3).zfill(2) + '00'
print(forecasthoursubback)
snowtotalsback = np.load('/gpfs_backup/stormtrack/jtradfor/ensemble_data/rawdata/sref/%s_asnow.npy' % (forecasthoursubback))

hsnows = []
for i in range(0,16):
	hsnows.append(snowtotals[i] - snowtotalsback[i])

hsnow_mean = np.mean(hsnows,axis=0)
hsnow_mean[hsnow_mean<0.25] = np.nan
hsnow_mean[hsnow_mean>2.0] = 2.0
hsnow_mean[-10:,:] = np.nan
hsnow_mean[:10,:] = np.nan
hsnow_mean[:,:10] = np.nan
hsnow_mean[:,-10:] = np.nan
im = m.imshow(hsnow_mean,zorder=2,interpolation='none',cmap='Blues',vmin=0.,vmax=2.0)
cbar = plt.colorbar(im,fraction=0.023,ticks=[0,.2,.4,.6,.8,1.0,1.2,1.4,1.6,1.8,2.0])
cbar.ax.yaxis.set_tick_params(color='w')
cbar.ax.set_yticklabels([0,.2,.4,.6,.8,1.0,1.2,1.4,1.6,1.8,2.0],color='w')
plt.box(False)
hsnowfil = '/gpfs_backup/stormtrack/jtradfor/ensemble_data/wxenviz.github.io/uploads/outimages/sref/%s_hweasd_mean.png' % (forecasthoursub)
plt.savefig(hsnowfil,facecolor='#101010',bbox_inches='tight',dpi=500)
plt.close()



