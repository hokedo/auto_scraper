#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import argparse

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('type', help='Type of the token you ar adding')
	return parser.parse_args()

mapping = { #HDFS tsv files
	"review_text" : 10, #from hotel4x.reivew
	"hotel_title" : 9 #from hotel4x.source
}

if __name__ == '__main__':
	args = parse_arguments()
	if args.type not in mapping.keys():
		raise Exception("Invalid type parameter")
	for line in sys.stdin:
		line = line.strip().split("\t")
		if len(line) >= mapping[args.type] and line[mapping[args.type]] is not None and line[mapping[args.type]] != '':
			for token in line[mapping[args.type]].split():
				print token


		