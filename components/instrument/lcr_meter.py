import asyncio
import logging
import pyvisa as visa  # Updated import to match example
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class LCRMeter:
    """
    Class to interact with an LCR meter instrument using VISA.
    Provides methods for configuration and Ls-Rs measurement.
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
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = self.timeout
            logger.info(f"Connected to instrument: {self.resource_name}")
            
            # Check instrument identity (useful for debugging)
            idn = self.instrument.query("*IDN?")
            logger.info(f"Instrument identification: {idn.strip()}")
            
            # Initialize to Ls-Rs mode explicitly at startup
            # Using the exact syntax from the example code
            await self.set_ls_rs_mode()
            
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
            # Use the exact syntax from the example for frequency
            self.instrument.write(':FREQuency:CW %G' % (frequency))
            self.instrument.write(f"VOLT {voltage}")
            await asyncio.sleep(0.1)  # Allow settings to take effect
            logger.debug(f"Configured instrument: Freq={frequency}Hz, Volt={voltage}V")
            return True
        except Exception as e:
            logger.error(f"Error configuring instrument: {e}")
            return False
            
    async def set_ls_rs_mode(self) -> bool:
        """Explicitly set the instrument to Ls-Rs mode using the example code pattern."""
        try:
            # Use the exact syntax from the example code
            type = 'LSRS'
            self.instrument.write(':FUNCtion:IMPedance:TYPE %s' % (type))
            await asyncio.sleep(0.2)
            
            # Verify the settings were applied by querying the current mode
            func_type = self.instrument.query(":FUNCtion:IMPedance:TYPE?").strip()
            
            if func_type == "L" or func_type == "LSRS":
                logger.info("Successfully set instrument to Ls-Rs mode")
                return True
            else:
                logger.error(f"Failed to set Ls-Rs mode. Current mode: {func_type}")
                return False
        except Exception as e:
            logger.error(f"Error setting Ls-Rs mode: {e}")
            return False
    
    async def measure_ls_rs(self, max_retries: int = 3) -> Tuple[float, float]:
        """
        Measure series inductance and resistance.
        
        Args:
            max_retries: Maximum number of retries on error
            
        Returns:
            Tuple of (inductance in H, resistance in Ω)
        """
        retry_count = 0
        while retry_count <= max_retries:
            try:
                # Make sure we're in the correct mode
                if retry_count > 0:
                    await self.set_ls_rs_mode()  # Re-set the mode if this is a retry
                
                # Trigger a new measurement
                self.instrument.write(":INIT:IMM")
                await asyncio.sleep(0.5)  # Give time for the measurement
                
                # Now fetch the measurement
                result = self.instrument.query("FETCH?")
                logger.debug(f"Raw measurement result: {result.strip()}")
                
                values = result.strip().split(',')
                if len(values) >= 2:
                    # Use the raw value in henries without conversion
                    L = float(values[0])  # Keep in henries (H)
                    Rs = float(values[1])
                    
                    # Basic sanity check on values (adjust thresholds as needed)
                    if L < 0 or Rs < 0 or L > 1e6 or Rs > 1e6:
                        raise ValueError(f"Measurement values out of expected range: L={L} H, Rs={Rs} Ω")
                    
                    return L, Rs
                raise ValueError(f"Unexpected response format from LCR meter: {result}")
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Measurement error (attempt {retry_count}/{max_retries+1}): {str(e)}")
                
                if retry_count <= max_retries:
                    await asyncio.sleep(1.0)  # Longer delay before retry
                else:
                    logger.error(f"Failed to measure Ls-Rs after {max_retries+1} attempts: {str(e)}")
                    return 0, 0  # Return zeros on complete failure