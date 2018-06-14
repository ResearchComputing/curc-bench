

config = {}

# Submit slurm option defaults
config['submit'] = {}
config['submit']['account'] = 'admin'
config['submit']['qos'] = 'admin'

# Reserve slurm option defaults
config['reserve'] = {}
config['reserve']['account'] = 'admin'
config['reserve']['users'] = ['jobl6604', 'holtat', 'joan5896']


# Included Tests
config['ior'] = {}
config['ior']['ior'] = "/projects/rcops/holtat/src/IOR/src/C/IOR"
config['ior']['modules'] = ['intel/17.4', 'impi/17.3', 'hdf5/1.10.1', 'netcdf/4.4.1.1', 'pnetcdf/1.8.1']


#
## First define the core switches
#SwitchName=OPACORE1 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE2 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE3 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE4 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE5 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE6 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE7 Switches=OPAEDGE[1-16]
#SwitchName=OPACORE8 Switches=OPAEDGE[1-16]

# Next define all the edge switches
# SwitchName=OPAEDGE1 Nodes=sgpu05[01-02],smem0501,shas05[01-28]
# SwitchName=OPAEDGE2 Nodes=shas06[33-64]
# SwitchName=OPAEDGE3 Nodes=smem0101,sgpu01[01-02],shas01[01-28]
# SwitchName=OPAEDGE4 Nodes=shas01[29-60]
# SwitchName=OPAEDGE5 Nodes=sknl07[01-20]
# SwitchName=OPAEDGE6 Nodes=shas06[05-32]
# SwitchName=OPAEDGE7 Nodes=smem0201,sgpu02[01-02],shas02[01-28]
# SwitchName=OPAEDGE8 Nodes=shas02[29-60]
# SwitchName=OPAEDGE9 Nodes=shas04[29-60]
# SwitchName=OPAEDGE10 Nodes=smem0401,sgpu04[01-02],shas04[01-28]
# SwitchName=OPAEDGE11 Nodes=shas05[29-60]
# SwitchName=OPAEDGE12 Nodes=shas03[29-60]
# SwitchName=OPAEDGE13 Nodes=smem0301,sgpu03[01-02],shas03[01-28]
# SwitchName=OPAEDGE14 Nodes=shas08[01-28],sgpu0801
# SwitchName=OPAEDGE15 Nodes=shas08[29-60]
# SwitchName=OPAEDGE16 Nodes=shas09[01-32]
# SwitchName=OPAEDGE17 Nodes=ssky09[33-52]
#
