import cv2
import cvutils
import numpy as np
import sqlite3
import math
import csv
import os.path
import subprocess
import random
import ConfigParser

setup_filename = 'setup.ini'
variable_parameters_filename = 'variableParameters.txt' 
static_parameters_filename = 'staticParameters.txt'

def config_mod(staParamArray, nConf, config0, config1, config2, config3, varParamArray, curr_params):
	for x in range(0,len(curr_params)):
		varParamArray[x].append(curr_params[x])
	for x in range(0,nConf):
		if x == 0:
			cfg = open(config0, 'w')
			cfg.write('# Automatically generated configuration file.')
			for spa in staParamArray:
				if int(spa[0]) == 0:
					cfg.write('\n')
					cfg.write(spa[1])
			for vpa in varParamArray:
				if int(vpa[0]) == 0:
					cfg.write('\n')
					cfg.write(vpa[1])
					cfg.write(' = ')
					cfg.write(str(vpa[-1]))
		if x == 1:
			cfg = open(config1, 'w')
			cfg.write('# Automatically generated configuration file.')
			for spa in staParamArray:
				if int(spa[0]) == 1:
					cfg.write('\n')
					cfg.write(spa[1])
			for vpa in varParamArray:
				if int(vpa[0]) == 1:
					cfg.write('\n')
					cfg.write(vpa[1])
					cfg.write(' = ')
					cfg.write(str(vpa[-1]))
		if x == 2:
			cfg = open(config2, 'w')
			cfg.write('# Automatically generated configuration file.')
			for spa in staParamArray:
				if int(spa[0]) == 2:
					cfg.write('\n')
					cfg.write(spa[1])
			for vpa in varParamArray:
				if int(vpa[0]) == 2:
					cfg.write('\n')
					cfg.write(vpa[1])
					cfg.write(' = ')
					cfg.write(str(vpa[-1]))
		if x == 3:
			cfg = open(config3, 'w')
			cfg.write('# Automatically generated configuration file.')
			for spa in staParamArray:
				if int(spa[0]) == 3:
					cfg.write('\n')
					cfg.write(spa[1])
			for vpa in varParamArray:
				if int(vpa[0]) == 3:
					cfg.write('\n')
					cfg.write(vpa[1])
					cfg.write(' = ')
					cfg.write(str(vpa[-1]))

def ConfigSectionMap(section):
	#Helps extract variables from the INI file
	dict1 = {}
	options = config.options(section)
	for option in options:
		try:
			dict1[option] = config.get(section, option)
			if dict1[option] == -1:
				DebugPrint("skip: $s" % option)
		except:
			print('exception on %s' % option)
			dict1[option] = None
	return dict1

def point_corresp_mod(pointcorr_name,current_elevation,homo_filename,elevdiff,gthomo_filename,shift_gt_homo):
	elevprop = []
	for ce in current_elevation:
		elevprop.append(float(ce)/1.5)

	pct = open(pointcorr_name,'r')
	fullextract = pct.readlines()
	pclines = fullextract[-6::]
	video_lines = []

	worldPts = []
	temp_holder = []

	#Extract latest point correspondences
	for j in range(0,2):
		temp_holder.append(pclines[j].split())

	#Extract world points
	for k in range(0,4):
		worldPts.append([float(temp_holder[0][k]),float(temp_holder[1][k])])

	worldPts2 = np.float32(worldPts)
	
	#Prepare video point arrays
	for x in range(2,6):
		video_lines.append(pclines[x].split())
		for y in range(0,4):
			video_lines[x-2][y] = video_lines[x-2][y].split('e+')

	point_arrays = []
	#each point:
	# [[X0, Y0]
	# [X1, Y1]]
	for a in range (0,4):
		point_arrays.append([[float(video_lines[0][a][0])*(10**float(video_lines[0][a][1])),
			float(video_lines[1][a][0])*(10**float(video_lines[1][a][1]))],
			[float(video_lines[2][a][0])*(10**float(video_lines[2][a][1])),
			float(video_lines[3][a][0])*(10**float(video_lines[3][a][1]))]])

	curr_videoPts = []
	curr_vidlower = []
	for i in range (0,4):
		delta_x = point_arrays[i][1][0] - point_arrays[i][0][0]
		delta_y = point_arrays[i][1][1] - point_arrays[i][0][1]
		a = math.sqrt((float(elevdiff)**2) / (1 + ((delta_x**2)/(delta_y**2))))
		b = a * (delta_x**2)/(delta_y**2)
		curr_videoPts.append([point_arrays[i][0][0] + (delta_x * elevprop[i]),point_arrays[i][0][1] + (delta_y * elevprop[i])])
		curr_vidlower.append([point_arrays[i][0][0] + ((1-b)*delta_x * elevprop[i]),point_arrays[i][0][1] + ((1-a) * delta_y * elevprop[i])])

	curr_videoPts2 = np.float32(curr_videoPts)
	currlower = np.float32(curr_vidlower)
	
	homography, mask = cv2.findHomography(np.array(curr_videoPts2), np.array(worldPts2))
	homography2, fail = cv2.findHomography(np.array(currlower), np.array(worldPts2))
	np.savetxt(homo_filename,homography)
	if shift_gt_homo == 1:
		np.savetxt(gthomo_filename,homography2)
	else:
		np.savetxt(gthomo_filename,homography)

#Read Setup file
config = ConfigParser.ConfigParser()
config.read(setup_filename)

nConfigs = int(ConfigSectionMap('ConfigFiles')['nconfigs'])
congif0 = ''
config1 = ''
config2 = ''
config3 = ''
if nConfigs == 1:
	config0 = ConfigSectionMap('ConfigFiles')['config0']
elif nConfigs == 2:
	config0 = ConfigSectionMap('ConfigFiles')['config0']
	config1 = ConfigSectionMap('ConfigFiles')['config1']
elif nConfigs == 3:
	config0 = ConfigSectionMap('ConfigFiles')['config0']
	config1 = ConfigSectionMap('ConfigFiles')['config1']
	config2 = ConfigSectionMap('ConfigFiles')['config2']
elif nConfigs == 4:
	config0 = ConfigSectionMap('ConfigFiles')['config0']
	config1 = ConfigSectionMap('ConfigFiles')['config1']
	config2 = ConfigSectionMap('ConfigFiles')['config2']
	config3 = ConfigSectionMap('ConfigFiles')['config3']
else:
	print 'Error : Invalid number of configuration files. The current maximum is 4.'
	a = 1/0

nrunlines = int(ConfigSectionMap('RunSettings')['nrunlines'])
runline0 = ''
runline1 = ''
runline2 = ''
runline3 = ''
if nrunlines == 1:
	runline0 = ConfigSectionMap('RunSettings')['runline0']
elif nrunlines == 2:
	runline0 = ConfigSectionMap('RunSettings')['runline0']
	runline1 = ConfigSectionMap('RunSettings')['runline1']
elif nrunlines == 3:
	runline0 = ConfigSectionMap('RunSettings')['runline0']
	runline1 = ConfigSectionMap('RunSettings')['runline1']
	runline2 = ConfigSectionMap('RunSettings')['runline2']
elif nrunlines == 4:
	runline0 = ConfigSectionMap('RunSettings')['runline0']
	runline1 = ConfigSectionMap('RunSettings')['runline1']
	runline2 = ConfigSectionMap('RunSettings')['runline2']
	runline3 = ConfigSectionMap('RunSettings')['runline3']
else:
	print 'Error : Invalid number of run-lines files. The current maximum is 4.'
	a = 1/0

no_homography = int(ConfigSectionMap('HomographyOptions')['no_homography'])
include_homo_altitude_mod = int(ConfigSectionMap('HomographyOptions')['include_homo_altitude_mod'])
shift_gt_homo = int(ConfigSectionMap('HomographyOptions')['shift_gt_homo'])
metersperpixel = float(ConfigSectionMap('HomographyOptions')['metersperpixel'])
homo_filename = str(ConfigSectionMap('HomographyOptions')['homo_filename'])
point_corr_filename = str(ConfigSectionMap('HomographyOptions')['point_corr_filename'])
gthomo_filename = str(ConfigSectionMap('HomographyOptions')['gthomo_filename'])
videoframefile = str(ConfigSectionMap('HomographyOptions')['videoframefile'])
worldfile = str(ConfigSectionMap('HomographyOptions')['worldfile'])

weight_mota = float(ConfigSectionMap('GeneralSettings')['weight_mota'])
max_iterations = int(ConfigSectionMap('GeneralSettings')['max_iterations'])
relative_change = float(ConfigSectionMap('GeneralSettings')['relative_change'])
max_n_changes = int(ConfigSectionMap('GeneralSettings')['max_n_changes'])
storage_filename = str(ConfigSectionMap('GeneralSettings')['storage_filename'])
video_filename = str(ConfigSectionMap('GeneralSettings')['video_filename'])
ground_truth_sqlite = str(ConfigSectionMap('GeneralSettings')['ground_truth_sqlite'])
sqlite_filename = str(ConfigSectionMap('GeneralSettings')['sqlite_filename'])

probConstant = float(ConfigSectionMap('OptimizationParameters')['prob_constant'])
t_init = float(ConfigSectionMap('OptimizationParameters')['t_init'])
max_match_dist = float(ConfigSectionMap('OptimizationParameters')['max_match_dist'])
lamda = float(ConfigSectionMap('OptimizationParameters')['lamda'])
emax = float(ConfigSectionMap('OptimizationParameters')['emax'])

#Extract Variable Parameters from .txt
varParams = open(variable_parameters_filename,'r')
lines = varParams.readlines()
varParamArray = []
for l in lines:
	temp = l.split(',')
	temp[-1] = temp[-1][:-1]
	varParamArray.append(temp)

#Extract Static Parameters from .txt
staParams = open(static_parameters_filename,'r')
lines = staParams.readlines()
staParamArray = []
for l in lines:
	temp = l.split(',')
	temp[-1] = temp[-1][:-1]
	staParamArray.append(temp)

solutions = []
with open(storage_filename, 'rb') as storagefile:
	csvreader = csv.reader(storagefile, delimiter=' ')
	for row in csvreader:
		solutions.append(row)

prevsol,prevelev,prevshift = [],[],[]
prevsol = solutions[(int(solutions[-1][-1]))+1][1:(len(varParamArray)+1)]

if include_homo_altitude_mod == 1:
	prevelev = solutions[(int(solutions[-1][-1]))+1][(len(prevsol)+1):(len(prevsol)+5)]
if shift_gt_homo == 1:
	prevshift = solutions[(int(solutions[-1][-1]))+1][-8]
else:
	prevshift = 0

currbest = solutions[(int(solutions[-1][-1]))+1]

if no_homography == 0:
	print 'Readjusting homography...'
	point_corresp_mod(point_corr_filename,prevsol,homo_filename,prevshift,gthomo_filename,shift_gt_homo)

print 'Preparing config files...'
config_mod(staParamArray, nConfigs, config0, config1, config2, config3, varParamArray, prevsol)

print ' '
print 'Good to go!'
print ' '
print "DON'T FORGET TO CHANGE THE VIDEO FILENAME IN THE CONFIG(S)"
print ' '