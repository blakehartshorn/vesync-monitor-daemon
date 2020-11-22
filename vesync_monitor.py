#!/usr/bin/env python3

import logging, logging.config, sys, time, yaml
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pyvesync import VeSync

with open('config.yaml','r') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config['Logging'])

logging.info("Starting VeSync monitoring daemon")

influx_client = InfluxDBClient(
    url=config['InfluxDB']['url'],
    token=config['InfluxDB']['token'],
    org=config['InfluxDB']['org']
)

influx_writer = influx_client.write_api(write_options=SYNCHRONOUS)

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

            influx_payload.append(
                Point("voltage")
                .tag("device_name", outlet.device_name)
                .field("value", outlet.voltage)
            )

            influx_payload.append(
                Point("power")
                .tag("device_name", outlet.device_name)
                .field("value", outlet.power)
            )

        logging.debug("Writing payload: %s", influx_payload)
        influx_writer.write(bucket=config['InfluxDB']['bucket'], record=influx_payload)
        time.sleep(config['Settings']['interval'])

    except Exception as e:
        logging.critical("Couldn't write payload",exc_info=True)
