import tablib
import os


dat_file = '/root/sim/python/data/exp/dat/pop9'
out_file = '/root/sim/python/data/exp/results/pop9'


def grab_important_data(dat_file, i, of=out_file):
    m_data = tablib.Dataset()
    i_data = tablib.Dataset()
    m_data.csv = open(dat_file, 'r').read()
    i_data.headers = m_data.headers[0:12]
    for line in m_data:
        i_data.append(line[0:12])
    f = of + '/final_data' + str(i) + '.txt'
    # f = './final_data/dat' + str(i) + '.txt'
    with open(f, 'w+') as w:
        w.write(i_data.csv)


def gid_wrapper(data_dir):
    count = 0
    for dir_name, subfile_list, file_list in os.walk(data_dir):
        for dfile in file_list:
            r_file = dir_name + '/' + dfile
            grab_important_data(r_file, count)
            count += 1
            print count
