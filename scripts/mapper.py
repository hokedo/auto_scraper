#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import argparse
from utils import hdfs_mapping

from utils import mapper_process

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('type', help='Type of the token you ar adding')
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_arguments()
	if args.type not in hdfs_mapping.keys():
		raise Exception("Invalid type parameter")
	for line in sys.stdin:
		mapper_process(line, args)


	