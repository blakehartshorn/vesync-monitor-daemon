# vesync-monitor-daemon
This is a small utility for monitoring Etekcity VeSync smart outlets and logging the power/voltage utilization to InfluxDB. Props to Mark Perdue for reverse engineering the API and making a python library available.

This has been rewritten for InfluxDB 2.0. Check out the influxdb1 branch for older versions.

Requirements:
* Python 3.6+
* InfluxDB 2.0
* PyYAML
* [pyvesync](https://github.com/markperdue/pyvesync)
