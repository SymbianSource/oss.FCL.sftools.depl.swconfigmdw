#!/bin/sh
rm -rf testlog.txt
find . -name "t_*" -exec {} >> testlog.txt \;
java -cp dbmsjdbctest.jar:dbmsjdbc.jar:junit.jar junit.textui.TestRunner com.symbian.dbms.jdbc.TestDbmsDriver >> testlog.txt
echo "Test results are stored in testlog.txt"
