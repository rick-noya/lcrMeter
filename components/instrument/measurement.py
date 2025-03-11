import asyncio
import logging
from datetime import datetime
from typing import List, Tuple, Any
from components.instrument.lcr_meter import LCRMeter

logger = logging.getLogger(__name__)

async def run_measurement_sequence(
    lcr_meter: LCRMeter,
    sample_name: str,
    tester_name: str
) -> List[List[Any]]:
    """
    Run a single Ls-Rs measurement on the LCR meter.
    
    Args:
        lcr_meter: Initialized LCR meter instance
        sample_name: Name of the sample being tested
        tester_name: Name of the person conducting the test
        
    Returns:
        List of measurement data rows in the format:
        [timestamp, sample_name, test_type, value1, value2, tester_name]
    """
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting Ls-Rs measurement for sample: {sample_name}, tester: {tester_name}")
    
    try:
        # Ensure we're in Ls-Rs mode
        await lcr_meter.set_ls_rs_mode()
        
        # Take a single measurement
        L, Rs = await lcr_meter.measure_ls_rs()
        
        # Log the measurement result
        logger.debug(f"Measurement: L={L:.3e} H, Rs={Rs:.3e} ohm")
        
        # Store the result
        results.append([timestamp, sample_name, "Ls-Rs", f"{L:.3e}", f"{Rs:.3e}", tester_name])
        
        logger.info("Ls-Rs measurement completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error during measurement sequence: {e}")
        raise