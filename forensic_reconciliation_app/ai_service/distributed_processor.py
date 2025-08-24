import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simulate_heavy_computation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a heavy computation task on a single data record.
    In a real distributed system, this would be a task executed on a worker node.
    """
    logging.info(f"Starting heavy computation for ID: {data.get('id', 'N/A')}")
    # Simulate CPU-bound work
    result = data.copy()
    processed_value = 0
    if 'payload' in result and 'transaction_amount' in result['payload']:
        try:
            amount = float(result['payload']['transaction_amount'])
            # A simple, arbitrary heavy computation
            for _ in range(int(amount / 10) + 1):
                processed_value += sum(i*i for i in range(1000))
            result['payload']['processed_amount'] = processed_value
            result['payload']['computation_status'] = 'completed'
        except (ValueError, TypeError):
            logging.warning(f"Transaction amount not suitable for computation for ID: {data.get('id', 'N/A')}")
            result['payload']['computation_status'] = 'skipped'
    else:
        result['payload']['computation_status'] = 'no_amount_found'

    time.sleep(0.1) # Simulate I/O or network latency
    logging.info(f"Finished heavy computation for ID: {data.get('id', 'N/A')}")
    return result

if __name__ == "__main__":
    from multiprocessing import Pool

    # Example usage with multiprocessing Pool
    sample_data_records = [
        {"id": "rec1", "payload": {"transaction_amount": 100}},
        {"id": "rec2", "payload": {"transaction_amount": 250}},
        {"id": "rec3", "payload": {"transaction_amount": 50}},
        {"id": "rec4", "payload": {"transaction_amount": 300}},
        {"id": "rec5", "payload": {"transaction_amount": 150}},
        {"id": "rec6", "payload": {"transaction_amount": "abc"}}, # Invalid data
    ]

    print("\n--- Simulating Distributed Processing ---")
    # Use a Pool to parallelize the computation
    # The number of processes should ideally be based on CPU cores
    with Pool(processes=4) as pool:
        # map applies the function to each item in the iterable
        processed_records = pool.map(simulate_heavy_computation, sample_data_records)

    for record in processed_records:
        print(f"Processed Record ID: {record['id']}, Computation Status: {record['payload'].get('computation_status')}")
