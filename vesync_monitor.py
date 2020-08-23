#!/usr/bin/env python3

import logging, logging.config, sys, time, yaml
from datetime import datetime
from influxdb import InfluxDBClient
from pyvesync import VeSync

with open('config.yaml','r') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config['Logging'])

logging.info("Starting VeSync monitoring daemon")

influx_client = InfluxDBClient(
    config['InfluxDB']['hostname'],
    config['InfluxDB']['port'],
    config['InfluxDB']['username'],
    config['InfluxDB']['password'],
    config['InfluxDB']['database']
)

vesync_client = VeSync(
    config['VeSync']['email'],
    config['VeSync']['password'],
    time_zone='America/New_York'
)

if not vesync_client.login():
    logging.critical("Could not login to VeSync")
    sys.exit(1)

while True:

    influx_payload = []

    try:
        logging.info("Updating energy information")
        vesync_client.update()
        vesync_client.update_energy()
        now = datetime.utcnow().isoformat()
    except Exception as e:
        logging.critical("No longer connected to VeSync", exc_info=True)
        sys.exit(1)

    try:
        for outlet in vesync_client.outlets:
            if outlet.voltage == 0:
                logging.warning("Could not determine voltage for %s. Is the outlet on?", outlet.device_name)
                continue
            influx_payload.append({
                "measurement": "voltage",
                "tags": {
                    "device_name": outlet.device_name,
                },
                "time": now,
                "fields": {
                    "value": outlet.voltage,
                }
            })
            influx_payload.append({
                "measurement": "power",
                "tags": {
                    "device_name": outlet.device_name,
                },
                "time": now,
                "fields": {
                    "value": outlet.power,
                }
            })

        logging.debug("Writing payload: %s", influx_payload)
        influx_client.write_points(influx_payload)
        time.sleep(config['Settings']['interval'])

    except Exception as e:
        logging.critical("Couldn't write payload",exc_info=True)
