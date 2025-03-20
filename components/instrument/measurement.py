import asyncio
import logging
from datetime import datetime
from typing import List, Tuple, Any, Dict
from components.instrument.lcr_meter import LCRMeter
from config.settings import GUI_VERSION

logger = logging.getLogger(__name__)

def validate_measurements(measurements: List[List[Any]]) -> Dict[str, Any]:
    """
    Validate measurement data before uploading to database or Notion.
    
    Args:
        measurements: List of measurement rows in the format:
                     [timestamp, sample_name, test_type, inductance, resistance, tester_name, gui_version]
                     
    Returns:
        Dict with keys:
            'valid': Boolean indicating if the measurements are valid
            'issues': List of issues found (empty if valid)
    """
    issues = []
    
    if not measurements:
        return {'valid': False, 'issues': ["No measurement data was collected"]}
    
    for row in measurements:
        # Check if we have the expected number of fields
        if len(row) < 5:  # We need at least timestamp, sample_name, test_type, inductance, resistance
            issues.append(f"Incomplete measurement data: {row}")
            continue
            
        # Extract inductance and resistance values
        try:
            inductance_str = row[3]  # Position of inductance value
            resistance_str = row[4]  # Position of resistance value
            
            # Convert scientific notation strings to float
            inductance = float(inductance_str)
            resistance = float(resistance_str)
            
            # Check if values are positive
            if inductance <= 0:
                issues.append(f"Invalid inductance value: {inductance_str} ≤ 0")
                
            if resistance <= 0:
                issues.append(f"Invalid resistance value: {resistance_str} ≤ 0")
                
        except (ValueError, TypeError) as e:
            issues.append(f"Error parsing measurement values: {e}")
            
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

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
        [timestamp, sample_name, test_type, inductance, resistance, tester_name, gui_version]
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
        
        # Store the result and include the gui_version
        results.append([
            timestamp, 
            sample_name, 
            "Ls-Rs", 
            f"{L:.3e}", 
            f"{Rs:.3e}", 
            tester_name,
            GUI_VERSION
        ])
        
        logger.info("Ls-Rs measurement completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error during measurement sequence: {e}")
        raise