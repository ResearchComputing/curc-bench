

config = {}

# Included Tests

# Node tests (linpack + stream)
config['node'] = {}
config['node']['linpack'] = "/curc/sw/intel/16.0.3/compilers_and_libraries_2016.3.210/linux/mkl/benchmarks/linpack/xlinpack_xeon64"
config['node']['stream'] = "/projects/rcops/CurcBenchBenchmarks/stream/stream.o"
config['node']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"

config['ior'] = {}
config['ior']['ior'] = "/projects/rcops/holtat/src/IOR/src/C/IOR"

# Bandwidth tests (osu_bw)
config['bandwidth'] = {}
config['bandwidth']['osu'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw"
config['bandwidth']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"

# Alltoall tests (osu_alltoall)
config['alltoall'] = {}
config['alltoall']['osu'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/collective/osu_alltoall"

config['alltoall-pair'] = {}
config['alltoall-pair']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"
config['alltoall-switch'] = {}
config['alltoall-switch']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"
config['alltoall-rack'] = {}
config['alltoall-rack']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"

# Alltoall rack test
config['Rack'] = {}
config['Rack']['Rack1'] = "shas01[01-60]"
config['Rack']['Rack2'] = "shas02[01-60]"
config['Rack']['Rack3'] = "shas03[01-60]"
config['Rack']['Rack4'] = "shas04[01-60]"
config['Rack']['Rack5'] = "shas05[01-60]"
config['Rack']['Rack6'] = "shas06[01-60]"
config['Rack']['Rack7'] = "shas07[01-16]"
config['Rack']['Rack8'] = "shas08[01-60]"
config['Rack']['Rack9'] = "shas09[01-28]"
config['Rack']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"


# Alltoall switch test
config['Switch'] = {}
config['Switch']['OPAEDGE1'] = "shas050[1-9],shas05[10-28]"
config['Switch']['OPAEDGE2'] = "shas06[33-64]"
config['Switch']['OPAEDGE3'] = "shas010[1-9],shas01[10-28]"
config['Switch']['OPAEDGE4'] = "shas01[29-60]"
config['Switch']['OPAEDGE5'] = "shas070[1-9],shas07[10-16]"
config['Switch']['OPAEDGE6'] = "shas060[1-9],shas06[10-32]"
config['Switch']['OPAEDGE7'] = "shas020[1-9],shas02[10-28]"
config['Switch']['OPAEDGE8'] = "shas02[29-60]"
config['Switch']['OPAEDGE9'] = "shas04[29-60]"
config['Switch']['OPAEDGE10'] = "shas040[1-9],shas04[10-28]"
config['Switch']['OPAEDGE11'] = "shas05[29-60]"
config['Switch']['OPAEDGE12'] = "shas03[29-60]"
config['Switch']['OPAEDGE13'] = "shas030[1-9],shas03[10-28]"
config['Switch']['OPAEDGE14'] = "shas08[01-28]"
config['Switch']['OPAEDGE15'] = "shas08[29-60]"
config['Switch']['OPAEDGE16'] = "shas09[01-28]"
config['Switch']['nodes'] = "shas[01-06][01-60],shas07[01-16],shas06[60-64],shas08[01-60],shas09[01-28]"



#
