import numpy as np
import pdb, glob, os
from netCDF4 import Dataset

##########
# this is a python2.7 program
# this code takes netCDF files downloaded from the CMIP5 archive and creates a file containing
# global and tropical average values for analysis in Dessler et al., ACP, 2018
# the program calls CDO, Climate Data Operators (https://code.mpimet.mpg.de/projects/cdo/), to
# manipulate the netCDF files.

dirx='/sn2/dessler/cmip5c/'
os.chdir(dirx)

# find models with both control and abrupt 4xCO2 runs
fn1=glob.glob('*.ta.piControl*nc')
models=[ii.split('.')[0] for ii in fn1]
fn1=glob.glob('*.ta.abrupt4xCO2*nc')
models2=[ii.split('.')[0] for ii in fn1]
models=list(set(models).intersection(set(models2))) 

for runType in ['piControl','abrupt4xCO2']:
    for modx in models:

        if os.path.exists('/home/dessler/energyBalance/cmip5temp/{0}.{1}.nc'.format(modx,runType)):
            print 'skipping: {1} {0}'.format(modx,runType)
            continue

        print '{} {}'.format(runType,modx)
        # calculate flux
        commandStr='cdo -merge {0}.rlut.{1}.r1.nc {0}.rsdt.{1}.r1.nc {0}.rsut.{1}.r1.nc {0}.rsutcs.{1}.r1.nc {0}.rlutcs.{1}.r1.nc ofile4.nc'.format(modx,runType)
        os.system(commandStr)
        
        # global average the fluxes
        commandStr='cdo -fldavg ofile4.nc ofile1.nc'
        os.system(commandStr)
        
        commandStr="cdo -expr,'flux=rsdt-rsut-rlut' ofile1.nc gflux.nc"
        os.system(commandStr)
        commandStr='cdo -f nc -t echam6 -expr,lwcre=rlut-rlutcs ofile1.nc ofile2.nc'
        os.system(commandStr)
        commandStr='cdo -f nc -t echam6 -expr,swcre=rsut-rsutcs ofile1.nc ofile3.nc'
        os.system(commandStr)
        
        commandStr="cdo merge ofile1.nc ofile2.nc ofile3.nc gflux.nc gflux3.nc"
        os.system(commandStr)
        os.system('rm -f ofile?.nc gflux.nc gflux2.nc')

        # get 2m global average T
        commandStr='cdo -f nc -fldavg {0}.tas.{1}.r1.nc tsg.nc'.format(modx,runType)
        os.system(commandStr)

        # get 500-hPa global average T
        commandStr='cdo -f nc -fldavg -select,level=50000 {0}.ta.{1}.r1.nc tag.nc'.format(modx,runType)
        os.system(commandStr)

        # get 2m tropical average T
        commandStr='cdo -f nc -fldavg -sellonlatbox,0,360,-30,30 {0}.tas.{1}.r1.nc tst.nc'.format(modx,runType)
        os.system(commandStr)

        # get 500-hPa tropical average T
        commandStr='cdo -f nc -fldavg -sellonlatbox,0,360,-30,30 -select,level=50000 {0}.ta.{1}.r1.nc tat.nc'.format(modx,runType)
        os.system(commandStr)

        # change names of tropical avg. fields
        os.system('cdo chname,tas,tas_trop tst.nc tst2.nc')
        os.system('cdo chname,ta,t_trop tat.nc tat2.nc')
        os.system('rm -f tst.nc tat.nc')

        # merge the files into one .nc file 
        os.system('cdo -f nc -merge gflux3.nc tag.nc tsg.nc tst2.nc tat2.nc /home/dessler/energyBalance/cmip5temp/{0}.{1}.nc'.format(modx,runType))

        # clean up
        os.system('rm -f gflux3.nc tag.nc tsg.nc tst2.nc tat2.nc')
        print '\n\n'
        
os.chdir('/home/dessler/energyBalance')



