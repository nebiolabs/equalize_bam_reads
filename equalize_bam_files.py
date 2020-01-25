__author__ = 'Brad Langhorst'

# determine number of reads in each file (using pysam to extract from idxstats)
# calculates ratios relative to smallest file
# calls sambamba to downsample

import sys
import pysam
import os
from subprocess import call
from distutils.spawn import find_executable
from functools import reduce


def get_num_reads(filename):
    num_reads = 0
    try:
        num_reads = reduce(lambda x, y: x + y,
                           [eval('+'.join(l.rstrip('\n').split('\t')[2:])) for l in pysam.idxstats(filename).split('\n') if len(l) > 0])
    except:
        sys.stderr.write("Unable to count reads in file: %s" % filename)
    return num_reads


if not find_executable('sambamba'):
    sys.stderr.write("sambamba must be available on the path.\n")
    exit(1)

files_by_size = {file: get_num_reads(file) for file in sys.argv[1:]}

if len(list(files_by_size.values())) < 2:
    sys.stderr.write("multiple bam files should be specified\n")
    exit(1)

min_read_count = min(files_by_size.values())

smallest_file = list(file for file, size in (list(files_by_size.items())) if size == min_read_count)[0]

files_by_frac = {file: (min_read_count * 1.0 / size) for file, size in list(files_by_size.items()) if file != smallest_file}

for file, frac in list(files_by_frac.items()):
    output_file = os.path.splitext(file)[0] + ".even_cov.bam"
    print("%s: %s" % (file, frac))
    call("sambamba view -p -f bam -s %s %s -o %s" % (frac, file, output_file))

os.symlink(smallest_file, os.path.splitext(smallest_file)[0] + ".even_cov.bam")  # smallest file needs no downsampling
