from sys import argv

if len(argv) == 1:
    print("""用法：$ %0 <输入文件夹> <输出文件名> [时间间隔]""")
    exit()

import imageio
from os import listdir
from os.path import join

indir = argv[1]
outfile = argv[2]

if len(argv) < 4:
    duration = 0.1
else:
    duration = float(argv[3])

frames = [imageio.imread(join(indir, i)) for i in listdir(indir)]
imageio.mimsave(outfile, frames, "GIF", duration=duration)
