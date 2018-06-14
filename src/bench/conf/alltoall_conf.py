
config = {}

# Alltoall tests (osu_alltoall)
config = {}
config['osu_a2a_path'] = "/projects/rcops/CurcBenchBenchmarks/osu5.3.2/libexec/osu-micro-benchmarks/mpi/collective/osu_alltoall"
config['modules'] = ['intel/17.4', 'impi/17.3']
config['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
# additional latency above the specified limit allowed
config['latency_factor'] = 1.55
# expected average osu_alltoall latency for each node count
config['osu_latencies'] = { 2:13613.5219632, 3:28375.5187868,
                       4:43137.5156105, 5:57899.5124341,
                       6:72661.5092577, 7:87423.5060814,
                       8:102185.502905, 9:116947.499729,
                       10:131709.496552, 11:146471.493376,
                       12:161233.4902, 13:175995.487023,
                       14:190757.483847, 15:205519.480671,
                       16:220281.477494, 17:235043.474318,
                       18:249805.471141, 19:264567.467965,
                       20:279329.464789, 21:294091.461612,
                       22:308853.458436, 23:323615.45526,
                       24:338377.452083, 25:353139.448907,
                       26:367901.445731, 27:382663.442554,
                       28:397425.439378, 29:412187.436202,
                       30:426949.433025, 31:441711.429849,
                       32:456473.426672, 33:471235.423496,
                       34:753806.42032, 35:753806.417143,
                       36:753806.413967, 37:753806.410791,
                       38:753806.407614, 39:753806.404438,
                       40:753806.401262, 50:456062.014488,
                       51:522754.035136, 52:589446.055784,
                       53:656138.076432, 54:722830.09708,
                       55:789522.117728, 56:856214.138376,
                       57:922906.159024, 58:989598.179672,
                       59:1056290.20032, 60:1122982.22097,
                       61:1189674.24162, 62:1256366.26226,
                       63:1323058.28291, 64:1389750.30356,
                       65:1456442.32421, 66:1523134.34486,
                       67:1589826.3655, 68:1656518.38615,
                       69:1723210.4068, 70:1789902.42745,
                       71:1856594.4481, 72:1923286.46874,
                       73:1989978.48939, 74:2056670.51004,
                       75:2123362.53069, 76:2190054.55134,
                       77:2256746.57198, 78:2323438.59263,
                       79:2390130.61328, 80:2456822.63393, }

# config['alltoall-pair'] = {}
# config['alltoall-pair']['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
# config['alltoall-switch'] = {}
# config['alltoall-switch']['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
# config['alltoall-rack'] = {}
# config['alltoall-rack']['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"

# Alltoall rack test
config['Rack'] = {}
config['Rack']['Rack1'] = "shas01[01-60]"
config['Rack']['Rack2'] = "shas02[01-60]"
config['Rack']['Rack3'] = "shas03[01-60]"
config['Rack']['Rack4'] = "shas04[01-60]"
config['Rack']['Rack5'] = "shas05[01-60]"
config['Rack']['Rack6'] = "shas06[05-64]"
config['Rack']['Rack8'] = "shas08[01-60]"
config['Rack']['Rack9'] = "shas09[01-32]"
# config['Rack']['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"

# Alltoall switch test
config['Switch'] = {}
config['Switch']['OPAEDGE1'] = "shas05[01-28]"
config['Switch']['OPAEDGE2'] = "shas06[33-64]"
config['Switch']['OPAEDGE3'] = "shas01[01-28]"
config['Switch']['OPAEDGE4'] = "shas01[29-60]"
config['Switch']['OPAEDGE6'] = "shas06[05-32]"
config['Switch']['OPAEDGE7'] = "shas02[01-28]"
config['Switch']['OPAEDGE8'] = "shas02[29-60]"
config['Switch']['OPAEDGE9'] = "shas04[29-60]"
config['Switch']['OPAEDGE10'] = "shas04[01-28]"
config['Switch']['OPAEDGE11'] = "shas05[29-60]"
config['Switch']['OPAEDGE12'] = "shas03[29-60]"
config['Switch']['OPAEDGE13'] = "shas03[01-28]"
config['Switch']['OPAEDGE14'] = "shas08[01-28]"
config['Switch']['OPAEDGE15'] = "shas08[29-60]"
config['Switch']['OPAEDGE16'] = "shas09[01-32]"
# config['Switch']['nodes'] = "shas[01-05][01-60],shas06[05-64],shas08[01-60],shas09[01-32]"
