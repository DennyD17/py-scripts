#!/usr/bin/sh -x 
. ~/.profile

#Vars
CheckDir="/etldata/Etlprd_BNK/FILESTORE/w4/Way4_from_filestore_UAT_Relese_2"
WorkDir="/home/fs_w4/W4checker"
MAILTO=''
count=0
HOST=
USER=
Password=
Curr_Time=`date +%H%M`
TIMESTAMP=`date +%Y%m%d%H%M`
send() {
/usr/sbin/sendmail -t << EOF
To: $MAILTO
From: "inform" <fs_w4@inform.cgs.sbrf.ru>
Subject:Way4 Check
$1

EOF
}



#Package date must be:
LastdateBadFormat=`perl -e "print scalar localtime (time -172800)"`
year=`echo $LastdateBadFormat | cut -f 5 -d " "`
month_lt=`echo $LastdateBadFormat | cut -f 2 -d " "`
day=`echo $LastdateBadFormat | cut -f 3 -d " "`
if [ $month_lt = 'Jan' ] 
  then 
    month=01
  fi
if [ $month_lt = 'Feb' ] 
  then 
    month=02
  fi 
if [ $month_lt = 'Mar' ] 
  then 
    month=03
  fi
if [ $month_lt = 'Apr' ] 
  then 
    month=04
  fi
if [ $month_lt = 'May' ] 
  then 
    month=05
  fi
if [ $month_lt = 'Jun' ] 
  then 
    month=06
  fi
if [ $month_lt = 'Jul' ] 
  then 
    month=07
  fi
if [ $month_lt = 'Aug' ] 
  then 
    month=08
  fi
if [ $month_lt = 'Sep' ] 
  then 
    month=09
  fi
if [ $month_lt = 'Oct' ] 
  then 
    month=10
  fi
if [ $month_lt = 'Nov' ] 
  then 
    month=11
  fi
if [ $month_lt = 'Dec' ] 
  then 
    month=12
  fi
NecDate=$year$month$day

#It was checked today?
if [ -f $WorkDir/$NecDate.flag ]
 then
   exit 0
 fi
 
  
#Connect to FTP and try to copy package whith necessary date 
cd $CheckDir
ftp -inv $HOST << EOF
user $USER $Password
cd /vol/vol1/FTP_PROD/OUT/Way4/Vrem
mget 016_000001_$NecDate*
EOF

files=`ls`

#check is there necessary files
if [ $files = ""]
  then 
    echo "Check at $TIMESTAMP : There are no files" >> $WorkDir/Way4CheckLOg.log
    exit 0
  fi

#Create logfile
touch $WorkDir/$NecDate.log
echo "Package_date="$NecDate>$WorkDir/$NecDate.log
#Count number of files
for i in $files
do
let count=$count+1  
done
echo "Number of files="$count >>$WorkDir/$NecDate.log
#check size of Tranz
trznz_size=`ls -l *tranz.000000* | awk '{print $5}'`
let tranz=$trznz_size/1048576
echo "Tranz_size="$tranz >>$WorkDir/$NecDate.log
#Check files for errors
for i in $files
  do 
    echo "Check file $i :" >> $WorkDir/$NecDate.log
    cat $i | grep "ERROR at line" >> $WorkDir/$NecDate.log 
    cat $i | grep "ORA-[0-9]\{5\}" >> $WorkDir/$NecDate.log 
  done

touch $WorkDir/$NecDate.flag
echo "Check at $TIMESTAMP : Way4 was checked">> $WorkDir/Way4CheckLOg.log


rm $CheckDir/*
 
info=`cat $WorkDir/$NecDate.log` 
send $info
 


