
config = {}

# Bandwidth tests (osu_bw)
config = {}
config['osu_bw_path'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw"
config['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
config['modules'] = ['intel/17.4', 'impi/17.3']

# Expected results
config['osu_bandwidths'] = {
    4194304: 10000.0,
    1048576: 10000.0,
    262144: 10000.0,
    65536: 6000.0,
}
