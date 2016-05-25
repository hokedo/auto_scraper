#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import argparse

sql_insert = "INSERT INTO tokens.all_tokens (token, type) SELECT '{0}', {1} WHERE NOT EXISTS (SELECT 1 from tokens.all_tokens WHERE token = '{0}');"

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('type', help='Type of the token you ar adding')
	return parser.parse_args()

mapping = { 
	"review_text" : 2,
	"hotel_title" : 1
}

if __name__ == '__main__':
	args = parse_arguments()
	if args.type not in mapping.keys():
		raise Exception("Invalid type parameter")
	print "BEGIN;"
	for line in sys.stdin:
		line = line.strip()
		line = repr(line)
		line.strip("'")
		print sql_insert.format(line, mapping[args.type])
	print "COMMIT;"
		
