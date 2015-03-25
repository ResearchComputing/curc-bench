import json
import re


def read_info_file(in_file):
    node_list = []
    line = in_file.readline()
    while line:
        if line.startswith('node'):
            node_list.append(line.strip())
        line = in_file.readline()
    return node_list


def rack(node_list):
    rack_switch = {}
    for node in node_list:
        rack_num = node[4:6]
        rack_name = 'infiniband_rack_' + str(rack_num)
        if rack_name not in rack_switch:
            rack_switch[rack_name] = []
        rack_switch[rack_name].append(node)
    return rack_switch


def rack_switch_18(node_list):
    rack_switch = json.load(open('/curc/admin/benchmarks/software/local_python/bench/util/rack_switch.json'))

    switch_dictionary = {'u42': '1', 'u43': '2', 'u44':'3', 'u45':'4', 'u46':'5'}

    for r in rack_switch.keys():
        result = re.match(r"(?P<id>\w+)-(?P<rack>\w+)-(?P<uid>\w+)", r)

        if r == 'Infiniscale-I':
            rack_name = 'infiniband_rack_07_5'
            rack_switch[rack_name] = rack_switch[r]
            del rack_switch[r]

        if result:
            name = result.group('rack')
            rack_num = "%02d" % (int(name.replace('rack','')),)
            switch_num = switch_dictionary[result.group('uid')]
            rack_name = 'infiniband_rack_' + rack_num + '_' + switch_num
            rack_switch[rack_name] = rack_switch[r]
            del rack_switch[r]

    count = 0
    keep = 0
    for r in rack_switch:
        previous = len(rack_switch[r])
        removelist = []
        for n in rack_switch[r]:
            if n not in node_list:
                removelist.append(n)
            else:
                keep += 1.0
        for x in removelist:
            rack_switch[r].remove(x)
        count += len(rack_switch[r])

    remove_list = []
    for r,l in rack_switch.iteritems():
        if len(l) < 1:
            remove_list.append(r)

    for r in remove_list:
        del rack_switch[r]

    tmp_11 = []
    tmp_13 = []
    try:
        for node in rack_switch['infiniband_rack_11_5']:
            if node[4:6] =='11':
                tmp_11.append(node)
            else:
                tmp_13.append(node)

        rack_switch['infiniband_rack_11_5'] = tmp_11
        rack_switch['infiniband_rack_13_6'] = tmp_13
    except:
        pass

    return rack_switch


def rack_switch_pairs(node_list):
    results = {}
    test = rack_switch_18(node_list)
    for name, name_list in test.iteritems():
        data = rack_list_subsets(name_list)
        results = dict(results.items() + data.items())

    return results


def rack_subsets(data, node_list):
    try:
        size = len(node_list)

        if size > 2:
            if size%2 == 0:
                for i in xrange(0,size-1,2):
                    list_string = 'set_'+str(i)+'_list'
                    name_string = 'set_'+str(i)+'_name'
                    data[list_string] = node_list[i]+","+node_list[i+1]
                    data[name_string] = node_list[i]+"_"+node_list[i+1]
            else:
                for i in xrange(0,size-2,2):
                    list_string = 'set_'+str(i)+'_list'
                    name_string = 'set_'+str(i)+'_name'
                    data[list_string] = node_list[i]+","+node_list[i+1]
                    data[name_string] = node_list[i]+"_"+node_list[i+1]
                index = size-2
                list_string = 'set_last_list'
                name_string = 'set_last_name'
                data[list_string] = node_list[index]+","+node_list[index+1]
                data[name_string] = node_list[index]+"_"+node_list[index+1]

    except:
        print "problem with %s", size


def rack_list_subsets(node_list):
    data = {}
    size = len(node_list)

    if size > 2:
        if size%2 == 0:
            for i in xrange(0,size-1,2):
                list_string = 'set_'+str(i)+'_list'
                list_string = 'infiniband_' + node_list[i] + '_' + node_list[i+1]
                data[list_string] = []
                data[list_string].append(node_list[i])
                data[list_string].append(node_list[i+1])

        else:
            for i in xrange(0,size-2,2):
                list_string = 'infiniband_' + node_list[i] + '_' + node_list[i+1]
                data[list_string] = []
                data[list_string].append(node_list[i])
                data[list_string].append(node_list[i+1])
            index = size-2
            list_string = 'infiniband_' + node_list[index] + '-' + node_list[index+1]
            data[list_string] = []
            data[list_string].append(node_list[index])
            data[list_string].append(node_list[index+1])

    elif size == 2:
        list_string = 'infiniband_' + node_list[0] + '_' + node_list[1]
        data[list_string] = node_list[:]

    return data
