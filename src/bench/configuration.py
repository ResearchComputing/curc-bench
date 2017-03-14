

config = {}

# Included Tests

# Node tests (linpack + stream)
config['node'] = {}
config['node']['linpack'] = "/curc/sw/intel/16.0.3/compilers_and_libraries_2016.3.210/linux/mkl/benchmarks/linpack/xlinpack_xeon64"
config['node']['stream'] = "/projects/holtat/cb_dev/stream/stream"

# Bandwidth tests (osu_bw)
config['bandwidth'] = {}
config['bandwidth']['osu'] = "/projects/molu8455/redhat_6/software/bandwidth/osu_bw"

# Alltoall tests (osu_alltoall)
config['alltoall'] = {}
config['alltoall']['osu'] = "/curc/admin/benchmarks/software/mpi/osu_alltoall"
