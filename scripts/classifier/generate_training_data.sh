#!/bin/bash

set -x
set -e

LIMIT=$1

if [ -z $LIMIT ]; 
then
	LIMIT="1000"
fi

if [ -f training_data.tsv ];
then
	rm	training_data.tsv
fi

touch training_data.tsv

token_table=('name' 'hotel4x.hotel' 'HOTEL_NAME'\
			 'address' 'hotel4x.hotel' 'HOTEL_ADDRESS'\
			 'author' 'hotel4x.review' 'REVIEW_AUTHOR'\
			 'title' 'hotel4x.review' 'REVIEW_TITLE'\
			 "array_to_string(token_array, '')" 'hotel4x.review' 'REVIEW_TEXT'\
			 'date' 'hotel4x.review' 'REVIEW_DATE'\
			 'score' 'hotel4x.review' 'REVIEW_SCORE')

for ((i=0; i<${#token_table[@]}; i+=3));
do   
	token_name=${token_table[i]}
	table_name=${token_table[i+1]}
	token_type=${token_table[i+2]}
	psql ty_analytic -U dev-ro -h db.trustyou.com \
	-c "COPY (SELECT $token_name, '$token_type' FROM $table_name WHERE char_length($token_name::text) > 0 and char_length($token_name::text) < 200 LIMIT $LIMIT) TO STDOUT WITH NULL AS ''"\
		>> training_data.tsv

done
