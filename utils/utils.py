import numpy as np

def convert(o):
    # https://bugs.python.org/issue24313
    # https://stackoverflow.com/a/50577730/9486169
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

def rows_to_pairs(l):
    # Converts [[1, 2, 3], [4, 5, 6]] to [[1,4], [2,5], [3,6]]
    m = list()
    if isinstance(l, list):
        for i in range(len(l[0])):
            m.append([l[0][i], l[1][i]])
    elif isinstance(l, np.ndarray):
        for i in range(l.shape[1]):
            m.append([convert(l[0,i]), convert(l[1,i])])
    return m

def pairs_to_rows(l):
    # Converts [[1,4], [2,5], [3,6]] to [[1, 2, 3], [4, 5, 6]]
    m = list()
    n = list()
    for i in range(len(l)):
        m.append(l[i][0])
        n.append(l[i][1])
    return [m, n]

def consolidate_name(s):
    return s.replace(' ', '_').replace(',', '_').replace('.', '_').replace(';', '_').replace(':', '_')

def read_out_pixels(img_stack, loc_dict, bands_of_interest):
    if loc_dict['px'].shape[1] > 0:
        M = np.multiply(img_stack[loc_dict['px'][0], loc_dict['px'][1], :], 10000).astype(np.int)
    else:
        M = np.empty((0,len(bands_of_interest)))
    return M
