import forged
import random
import time
import logging

def measure_normal(mean=0.0, sigma=1.0) -> float:
    return random.gauss(mu=mean, sigma=sigma)

def measure_current() -> float:
    """ Measures current at 350mA with 50mA standard deviation. """
    return measure_normal(0.35, sigma=0.050)

def measure_voltage(mean=5, tol=0.1) -> float:
    return measure_normal(mean, sigma=tol/3)


def main():
    # Upload a serial number
    forged.upload_value("serial_number", "SimulatedSerialNumber")

    # Upload some measurements
    # TODO: Actually measure voltage and current using a DMM.
    logging.info("Measuring hardware values")
    time.sleep(3)
    forged.upload_value("vcc", measure_voltage())
    time.sleep(0.1)
    forged.upload_value("current", measure_current())
    time.sleep(0.1)

    # TODO: Maybe have the firmware upload these instead?
    logging.info("Recording firmware information...")
    time.sleep(3)
    forged.upload_value("hardware_version", "v1.1")
    time.sleep(0.1)
    forged.upload_value("boot_duration", measure_normal(mean=0.1, sigma=0.05))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
