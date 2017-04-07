

config = {}

# Included Tests

# Node tests (linpack + stream)
config['node'] = {}
config['node']['linpack'] = "/curc/sw/intel/16.0.3/compilers_and_libraries_2016.3.210/linux/mkl/benchmarks/linpack/xlinpack_xeon64"
config['node']['stream'] = "/projects/rcops/CurcBenchBenchmarks/stream/stream.o"

# Bandwidth tests (osu_bw)
config['bandwidth'] = {}
config['bandwidth']['osu'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw"

# Alltoall tests (osu_alltoall)
config['alltoall'] = {}
config['alltoall']['osu'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/collective/osu_alltoall"

# Alltoall rack test
config['alltoall']['Rack'] = {}
config['alltoall']['Rack']['Rack1'] = "shas01[01-60]"
config['alltoall']['Rack']['Rack2'] = "shas02[01-60]"
config['alltoall']['Rack']['Rack3'] = "shas03[01-60]"
config['alltoall']['Rack']['Rack4'] = "shas04[01-60]"
config['alltoall']['Rack']['Rack5'] = "shas05[01-60]"
config['alltoall']['Rack']['Rack6'] = "shas06[01-60]"
config['alltoall']['Rack']['Rack7'] = "shas07[01-16]"

# Alltoall switch test
config['alltoall']['Switch'] = {}
config['alltoall']['Switch']['OPAEDGE1'] = "shas050[1-9],shas05[10-28]"
config['alltoall']['Switch']['OPAEDGE2'] = "shas06[33-64]"
config['alltoall']['Switch']['OPAEDGE3'] = "shas010[1-9],shas01[10-28]"
config['alltoall']['Switch']['OPAEDGE4'] = "shas01[29-60]"
config['alltoall']['Switch']['OPAEDGE5'] = "shas070[1-9],shas07[10-16]"
config['alltoall']['Switch']['OPAEDGE6'] = "shas060[1-9],shas06[10-32]"
config['alltoall']['Switch']['OPAEDGE7'] = "shas020[1-9],shas02[10-28]"
config['alltoall']['Switch']['OPAEDGE8'] = "shas02[29-60]"
config['alltoall']['Switch']['OPAEDGE9'] = "shas04[29-60]"
config['alltoall']['Switch']['OPAEDGE10'] = "shas040[1-9],shas04[10-28]"
config['alltoall']['Switch']['OPAEDGE11'] = "shas05[29-60]"
config['alltoall']['Switch']['OPAEDGE12'] = "shas03[29-60]"
config['alltoall']['Switch']['OPAEDGE13'] = "shas030[1-9],shas03[10-28]"
