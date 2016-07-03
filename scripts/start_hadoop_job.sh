#!/bin/bash


usage()
{
cat << EOF
  Usage: $0 -t <token_type> -[-p <script_part>]

  Runs a hadoop job to collect tokens and generate inserts.

  OPTIONS:
    -h    Show this message.
    -t    The type of the token needed. Ex: hotel_title, review_text etc
    -p    The part of this script to run.
    	  First part: Grep and sort them uniquely

  Accepted token types: hotel_title, review_text

  Examples:

    $ $0 -t hotel_title -p all

EOF
}

mappings()
{	
	
	INPUT=""
	token_type=$1;
	if [ "$token_type" == "hotel_title" ]; then
        INPUT="";

	elif [ "$token_type" == "review_text" ]; then
        INPUT="";
    else
    	echo -e "\n Invalid token type \n"
        usage >&2
    	exit 1
    fi

echo "input: $INPUT"

}

set_params()
{
TYPE=""
PART=""
VERBOSE=""
        while getopts "h:t:p:v" OPTION
        do
                case "$OPTION" in
                        h)
                                usage >&2
                                exit
                                ;;
                        t)
                                TYPE="$OPTARG"
                                ;;
                        p)
                                PART="$OPTARG"
                                ;;
                        ?)
                                usage >&2
                                exit 1
                                ;;
                esac
        done

        if [ -z "$TYPE" ]; then
                echo -e "\n Token type not specified \n" >&2
                usage >&2
                exit 1
        fi

        if [ -z "$PART" ] || [ "$PART" == "0" ] || [ "$PART" == "all" ] ; then
                PART="all";
        fi

        if [ "$PART" == "1" ] || [ "$PART" == "first" ] ; then
                PART="first";
        fi

        if [ "$PART" == "2" ] || [ "$PART" == "second" ] ; then
                PART="second";
        fi

        echo "type: $TYPE"
        echo "part: $PART"
}

set_params $@
mappings $TYPE

if [ "$PART" == "all" ] || [ "$PART" == "first" ] ; then
    hadoop jar /usr/local/hadoop/contrib/streaming/hadoop-*-streaming.jar\
        -Dstream.non.zero.exit.is.failure=false\
        -Dmapred.map.tasks.speculative.execution=false\
        -Dmapred.reduce.tasks=500\
        -file "mapper.py"\
        -file "utils.py"\
        -input "$INPUT"\
        -output "crawl-gen/$TYPE""_temp"\
        -mapper "mapper.py $TYPE"\
        -reducer "sort -u"
    fi
if [ "$PART" == "all" ] || [ "$PART" == "second" ] ; then
    hadoop jar /usr/local/hadoop/contrib/streaming/hadoop-*-streaming.jar\
        -Dstream.non.zero.exit.is.failure=false\
        -Dmapred.map.tasks.speculative.execution=false\
        -Dmapred.reduce.tasks=0\
        -file "generate_inserts.py"\
        -file "utils.py"\
        -input "crawl-gen/$TYPE""_temp"\
        -output "crawl-gen/$TYPE"\
        -mapper "generate_inserts.py $TYPE"
    fi