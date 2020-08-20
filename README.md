# vesync-monitor-daemon
This is a small utility for monitoring Etekcity VeSync smart outlets and logging the power/voltage utilization to InfluxDB. Props to Mark Perdue for reverse engineering the API and making a python library available.

Requirements:
* Python 3.5+
* InfluxDB 1.4+
* PyYAML
* [pyvesync](https://github.com/markperdue/pyvesync)

Recommended:
* Grafana

