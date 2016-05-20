#!/bin/bash

update_type=$1

if [ ! -z $update_type ] && [ $update_type == 'push' ];
then
	echo "Pushing to server"
	scp -r /home/hokedo/Work/crawling-generator/* hokedo@82.79.64.138:./Projects/crawling-generator/
else 
	echo "Retrieving files from server"
	scp -r hokedo@82.79.64.138:./Projects/crawling-generator/* .
fi

