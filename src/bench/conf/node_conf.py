
config = {}

# Node tests (linpack + stream)
config['linpack_path'] = "/curc/sw/intel/16.0.3/compilers_and_libraries_2016.3.210/linux/mkl/benchmarks/linpack/xlinpack_xeon64"
config['stream_path'] = "/projects/rcops/CurcBenchBenchmarks/stream/stream.o"
config['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
config['modules'] = ['intel']

# Expected results
config['stream_copy'] = 88000.0
config['stream_scale'] = 89000.0
config['stream_add'] = 91000.0
config['stream_triad'] = 92000.0
config['linpack_averages'] = {
                (5000, 5000, 4): 380.0,
                (10000, 10000, 4): 580.0,
                (20000, 20000, 4): 670.0,
                (25000, 25000, 4): 640.0 }
