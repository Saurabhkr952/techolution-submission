#!/usr/bin/env python3
import requests
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def make_request(url, request_num):
    try:
        start = time.time()
        response = requests.get(url, timeout=10, verify=True)
        duration = time.time() - start
        return {'status': response.status_code, 'duration': duration}
    except Exception as e:
        return {'status': 'error', 'duration': 0, 'error': str(e)}

def run_load_test(url, concurrency, duration):
    print(f"Starting load test...")
    print(f"URL: {url}")
    print(f"Concurrency: {concurrency}")
    print(f"Duration: {duration}s")
    print("-" * 50)
    
    start_time = time.time()
    end_time = start_time + duration
    request_count = 0
    success_count = 0
    error_count = 0
    total_duration = 0
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        while time.time() < end_time:
            futures = []
            for _ in range(concurrency):
                if time.time() >= end_time:
                    break
                future = executor.submit(make_request, url, request_count)
                futures.append(future)
                request_count += 1
            
            for future in as_completed(futures):
                result = future.result()
                if result['status'] == 200:
                    success_count += 1
                    total_duration += result['duration']
                else:
                    error_count += 1
                    if error_count == 1:
                        print(f"First error: {result.get('error', 'Unknown')}")
                
                if request_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rps = request_count / elapsed if elapsed > 0 else 0
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Requests: {request_count} | Success: {success_count} | Errors: {error_count} | RPS: {rps:.2f}")
    
    total_time = time.time() - start_time
    avg_response_time = total_duration / success_count if success_count > 0 else 0
    
    print("-" * 50)
    print(f"Load test completed!")
    print(f"Total requests: {request_count}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests per second: {request_count / total_time:.2f}")
    print(f"Average response time: {avg_response_time:.4f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HTTP Load Testing Script')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--concurrency', type=int, default=50, help='Number of concurrent requests')
    parser.add_argument('--duration', type=int, default=120, help='Test duration in seconds')
    
    args = parser.parse_args()
    run_load_test(args.url, args.concurrency, args.duration)
