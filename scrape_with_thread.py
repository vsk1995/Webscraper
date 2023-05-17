import requests
from bs4 import BeautifulSoup
import csv
from time import sleep, perf_counter
from concurrent import futures
from requests import RequestException  

# lists
urls=[]
URL = "give website url here"

#Configuraton
MAX_WORKERS = 20 
page_num = 100
max_retries = 2
time_out = 3

start_time = perf_counter()
print("Scraping starts now...\n")

def get(site):
    retries = 0
    while retries < max_retries:   
        try:
            # getting the request from url
            r = requests.get(site, timeout= time_out)
            return r
        except RequestException as e:
            print (e)
            retries += 1
            
def scrape(site):
    r = get (site)
    s = BeautifulSoup(r.text,"html.parser")
    for i in s.find_all("a"):
        try:  
            href = i.attrs['href']
        except KeyError:
            pass    
        if href.startswith("/"):
            site = URL+href
                        
            if site not in  urls and len(urls) < page_num:
                urls.append(site) 
                print(site)
                # calling itself
                scrape(site)
    return urls

# Create a CSV file and write headers
def write_csv(url):
    with open('scrape_with_thread.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title, h1, and h2 texts
        title = soup.title.string if soup.title else ''
        h1 = soup.find('h1').get_text() if soup.find('h1') else ''
        h2 = [tag.get_text() for tag in soup.find_all('h2')]

        # Get the size of the HTML content in bytes
        html_size = len(response.content)

        # Get the response code
        response_code = response.status_code

        # Get the time to download the page in seconds
        download_time = response.elapsed.total_seconds()

        # Write the data to the CSV file
        writer.writerow([url, title, h1, h2, response_code, html_size, download_time])

def csv_run(urls):
    workers = min(MAX_WORKERS, len(urls))
    with futures.ThreadPoolExecutor(workers) as executor:
        executor.map(write_csv, urls)

if __name__ == '__main__':
    urlss = scrape(URL)
    csv_run(urlss)

print('\nWriting data into a CSV file')
print('\nCSV file created successfully.')
end_time = perf_counter()
        
print(f'\nIt took {end_time- start_time: 0.2f} second(s) to complete scraping.')