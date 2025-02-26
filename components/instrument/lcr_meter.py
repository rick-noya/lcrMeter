import asyncio
import logging
import pyvisa
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class LCRMeter:
    """
    Class to interact with an LCR meter instrument using VISA.
    Provides methods for configuration and measurement.
    """
    
    def __init__(self, resource_name: str, timeout: int = 10000):
        self.resource_name = resource_name
        self.timeout = timeout
        self.instrument = None
        self.rm = None
        
    async def connect(self) -> bool:
        """
        Connect to the LCR meter.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = self.timeout
            logger.info(f"Connected to instrument: {self.resource_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to instrument: {e}")
            return False
            
    def close(self):
        """Close the connection to the instrument."""
        if self.instrument:
            self.instrument.close()
            logger.debug("Instrument connection closed")
        if self.rm:
            self.rm.close()
            logger.debug("Resource manager closed")
            
    async def configure(self, frequency: float, voltage: float):
        """
        Configure the instrument with frequency and voltage parameters.
        
        Args:
            frequency: Measurement frequency in Hz
            voltage: Measurement voltage in V
        """
        if not self.instrument:
            logger.error("Cannot configure: Not connected to instrument")
            return False
            
        try:
            self.instrument.write(f"FREQ {frequency}")
            self.instrument.write(f"VOLT {voltage}")
            self.instrument.write("TRIG:SOUR BUS")
            self.instrument.write("TRIG:IMM")
            await asyncio.sleep(0.1)  # Allow settings to take effect
            logger.debug(f"Configured instrument: Freq={frequency}Hz, Volt={voltage}V")
            return True
        except Exception as e:
            logger.error(f"Error configuring instrument: {e}")
            return False
            
    async def measure_ls_rs(self) -> Tuple[float, float]:
        """
        Measure series inductance and resistance.
        
        Returns:
            Tuple[float, float]: Inductance in µH and resistance in Ohms
        """
        try:
            self.instrument.write(":FUNCtion:IMPedance:TYPE L")
            await asyncio.sleep(0.1)
            result = await asyncio.to_thread(self.instrument.query, "FETCH?")
            values = result.strip().split(',')
            if len(values) >= 2:
                L = float(values[0]) * 1e6  # Convert H to µH
                Rs = float(values[1])
                return (L, Rs)
            else:
                logger.warning("Unexpected response format for Ls-Rs")
                return (0, 0)
        except Exception as e:
            logger.error(f"Error measuring Ls-Rs: {e}")
            return (0, 0)

    async def measure_cs_rs(self) -> Tuple[float, float]:
        """
        Measure series capacitance and resistance.
        
        Returns:
            Tuple[float, float]: Capacitance in nF and resistance in Ohms
        """
        try:
            self.instrument.write(":FUNCtion:IMPedance:TYPE C")
            await asyncio.sleep(0.1)
            result = await asyncio.to_thread(self.instrument.query, "FETCH?")
            values = result.strip().split(',')
            if len(values) >= 2:
                Cs = float(values[0]) * 1e9  # Convert F to nF
                Rs = float(values[1])
                return (Cs, Rs)
            else:
                logger.warning("Unexpected response format for Cs-Rs")
                return (0, 0)
        except Exception as e:
            logger.error(f"Error measuring Cs-Rs: {e}")
            return (0, 0)

    async def measure_cp_rp(self) -> Tuple[float, float]:
        """
        Measure parallel capacitance and resistance.
        
        Returns:
            Tuple[float, float]: Capacitance in nF and resistance in Ohms
        """
        try:
            self.instrument.write(":FUNCtion:IMPedance:TYPE C")
            self.instrument.write(":CALCulate:IMPedance:CIRcuit PARallel")
            await asyncio.sleep(0.1)
            result = await asyncio.to_thread(self.instrument.query, "FETCH?")
            values = result.strip().split(',')
            if len(values) >= 2:
                Cp = float(values[0]) * 1e9  # Convert F to nF
                Rp = float(values[1])
                return (Cp, Rp)
            else:
                logger.warning("Unexpected response format for Cp-Rp")
                return (0, 0)
        except Exception as e:
            logger.error(f"Error measuring Cp-Rp: {e}")
            return (0, 0)

    async def measure_resistance(self) -> float:
        """
        Perform a four-terminal resistance measurement.
        
        Returns:
            float: Resistance value in Ohms
        """
        try:
            self.instrument.write(":MEASure:RESistance?")
            await asyncio.sleep(0.1)
            ohm_result = await asyncio.to_thread(self.instrument.read)
            return float(ohm_result.strip())
        except Exception as e:
            logger.error(f"Error measuring 4pt Ohm: {e}")
            return 0