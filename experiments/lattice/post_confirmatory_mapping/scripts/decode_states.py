import numpy as np
N=24
def decode(packed):
    return np.where(np.unpackbits(packed,axis=-1,count=N,bitorder='little')>0,1,-1).astype(np.int8)
