#!/bin/bash
echo "Starting HBase container..."
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=/usr/local/hbase/bin:$PATH

sleep 300

echo "Starting HBase Master..."
/usr/local/hbase/bin/hbase master start &

echo "Starting HBase RegionServer..."
/usr/local/hbase/bin/hbase regionserver start &

echo "Starting HBase Thrift Server..."
/usr/local/hbase/bin/hbase thrift start &

echo "HBase services started, keeping container alive..."
tail -f /dev/null