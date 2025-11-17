import asyncio
import random
import logging

from forged import Forged

def measure_normal(mean=0.0, sigma=1.0) -> float:
    return random.gauss(mu=mean, sigma=sigma)

def measure_current() -> float:
    """ Measures current at 350mA with 50mA standard deviation. """
    return measure_normal(0.35, sigma=0.050)

def measure_voltage(mean=5, tol=0.1) -> float:
    return measure_normal(mean, sigma=tol/3)


async def main():

    # Upload a serial number
    await Forged.upload_value("serial_number", "SimulatedSerialNumber")

    # Upload some measurements
    await Forged.upload_value("vcc", measure_voltage())
    await Forged.upload_value("current", measure_current())
    await Forged.upload_value("hardware_version", "v1.1")
    await Forged.upload_value("boot_duration", measure_normal(mean=0.1, sigma=0.05))
    await Forged.upload_block("samples", {'values': [int(measure_normal(mean=50, sigma=10)) for _ in range(5)] })

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
