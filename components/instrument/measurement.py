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
    Run the complete measurement sequence on the LCR meter.
    
    Args:
        lcr_meter: Initialized LCR meter instance
        sample_name: Name of the sample being tested
        tester_name: Name of the person conducting the test
        
    Returns:
        List of measurement data rows in the format:
        [timestamp, sample_name, test_type, value1, value2]
    """
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting measurement sequence for sample: {sample_name}, tester: {tester_name}")
    
    try:
        # --- Test 1: Ls-Rs (Series Inductance & Resistance) ---
        L, Rs = await lcr_meter.measure_ls_rs()
        results.append([timestamp, sample_name, "Ls-Rs", f"{L:.3f} µH", f"{Rs:.3f} Ω"])
        logger.debug(f"Ls-Rs measurement: {L:.3f} µH, {Rs:.3f} Ω")
        
        # --- Test 2: Cs-Rs (Series Capacitance & Resistance) ---
        Cs, Rs = await lcr_meter.measure_cs_rs()
        results.append([timestamp, sample_name, "Cs-Rs", f"{Cs:.3f} nF", f"{Rs:.3f} Ω"])
        logger.debug(f"Cs-Rs measurement: {Cs:.3f} nF, {Rs:.3f} Ω")
        
        # --- Test 3: Cp-Rp (Parallel Capacitance & Resistance) ---
        Cp, Rp = await lcr_meter.measure_cp_rp()
        results.append([timestamp, sample_name, "Cp-Rp", f"{Cp:.3f} nF", f"{Rp:.3f} Ω"])
        logger.debug(f"Cp-Rp measurement: {Cp:.3f} nF, {Rp:.3f} Ω")
        
        # --- Test 4: 4pt Ohm (Four-terminal resistance measurement) ---
        ohm_result = await lcr_meter.measure_resistance()
        results.append([timestamp, sample_name, "4pt Ohm", f"{ohm_result:.3f} Ω", ""])
        logger.debug(f"4pt Ohm measurement: {ohm_result:.3f} Ω")
        
        # Add tester name to each row
        for row in results:
            row.append(tester_name)
            
        logger.info("Measurement sequence completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error during measurement sequence: {e}")
        raise
    finally:
        # Always close the connection to the instrument
        lcr_meter.close()