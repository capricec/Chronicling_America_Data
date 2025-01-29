import requests
import json

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
    all_items = []
    current_page = 1
    total_items = None
    
    # Keep fetching until we have all results
    while True:
        results = search_chronicling_america(
            query="",
            state="",
            date1="01-29-1925",
            date2="01-29-1925",
            page=current_page
        )
        
        # Store total items count from first request
        if total_items is None:
            total_items = results['totalItems']
            #total_items = 19
            print(f"Total items to fetch: {total_items}")
        
        # Add items from this page to our collection
        all_items.extend(results['items'])
        
        # Print progress
        print(f"Fetched page {current_page}, got {len(results['items'])} items. Total so far: {len(all_items)}")
        
        # Check if we've got all items or if there are no more results
        if len(results['items']) == 0 or len(all_items) >= total_items:
            break
            
        current_page += 1
    
    print(f"\nFinished! Retrieved {len(all_items)} total items")
    
    # Save all results to a text file
    with open('search_results.txt', 'w', encoding='utf-8') as f:
        # Write total number of results
        f.write(f"Found {len(all_items)} results\n\n")
        
        # Write details for each item
        for item in all_items:
            print(item)
            f.write(f"Title: {item['title']}\n")
            f.write(f"Date: {item['date']}\n")
            f.write(f"URL: {item['url']}\n")

            if 'ocr_eng' in item:
                f.write(f"Text: {item['ocr_eng']}\n")
            f.write("-" * 50 + "\n\n")  # Add a separator between entries