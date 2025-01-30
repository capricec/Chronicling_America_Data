import requests
import json
from datetime import datetime, timedelta
import time
import os

def search_chronicling_america(query, state=None, dateFilterType=None, date1=None, date2=None,searchType=None, page=1):
    """
    Perform an advanced search on the Chronicling America API
    
    Args:
        query (str): Search terms
        state (str, optional): Two-letter state code
        dateFilterType (str, optional): 'range' or 'exact'
        date1 (str, optional): Start date in YYYY-MM-DD format
        date2 (str, optional): End date in YYYY-MM-DD forma
        page (int): Page number of results
    
    Returns:
        dict: JSON response from the API
    """
    base_url = "https://chroniclingamerica.loc.gov/search/pages/results/"
    
    # Build parameters
    params = {
        'andtext': query,
        'format': 'json',
        'page': page,
        'searchType': 'advanced'
    }
    
    if state:
        params['state'] = state
    if date1:
        params['dateFilterType'] = 'range'
        params['date1'] = date1.replace('-', "/")
    if date2:
        params['date2'] = date2.replace('-', "/")
        
    # Make the request
    response = requests.get(base_url, params=params)
    print(response.url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

# Example usage
if __name__ == "__main__":
    # Define date range for 1925
    start_date = datetime(1925, 9, 28)
    end_date = datetime(1925, 12, 31)
    current_date = start_date
    
    # Create directory if it doesn't exist
    os.makedirs("1925_results", exist_ok=True)
    
    while current_date <= end_date:
        # Format the date as required for the API (MM-DD-YYYY)
        search_date = current_date.strftime("%m-%d-%Y")
        filename = f'1925_results/search_results_{search_date.replace("-", "_")}.txt'
        
        print(f"\nProcessing date: {search_date}")
        
        all_items = []
        current_page = 1
        total_items = None
        
        # Keep fetching until we have all results for current date
        while True:
            results = search_chronicling_america(
                query="",
                state="",
                date1=search_date,
                date2=search_date,
                page=current_page
            )
            
            # Store total items count from first request
            if total_items is None:
                total_items = results['totalItems']
                print(f"Total items to fetch: {total_items}")
            
            # Add items from this page to our collection
            all_items.extend(results['items'])
            
            # Print progress
            print(f"Fetched page {current_page}, got {len(results['items'])} items. Total so far: {len(all_items)}")
            
            # Check if we've got all items or if there are no more results
            if len(results['items']) == 0 or len(all_items) >= total_items:
                break
                
            current_page += 1
            time.sleep(0.5)  # Add a small delay between requests
        
        print(f"Finished! Retrieved {len(all_items)} total items for {search_date}")
        
        # Save results for this date to a text file
        with open(filename, 'w', encoding='utf-8') as f:
            # Write total number of results
            f.write(f"Found {len(all_items)} results\n\n")
            
            # Write details for each item
            for item in all_items:
                f.write(f"Title: {item['title']}\n")
                f.write(f"Date: {item['date']}\n")
                f.write(f"URL: {item['url']}\n")
                if 'ocr_eng' in item:
                    f.write(f"Text: {item['ocr_eng']}\n")
                f.write("-" * 50 + "\n\n")  # Add a separator between entries
        
        # Move to next day
        current_date += timedelta(days=1)
        time.sleep(1)  # Add a delay between processing different dates