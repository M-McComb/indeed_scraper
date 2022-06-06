"""
This is a first try at web scraping in python
It requires the bs4 and requests libraries

Future improvements would include:
    - integration into a tabular format and a SQL server (I am currently working on this!)
    - abstraction! Due to the relative simplicity here, it didn't really seem worth it!
    - better control of ending the scraping. Currently just has a set number of pages to scrape.
Written by Matthew McComb June 6th, 2022
"""
from datetime import datetime
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup as bs

#Request User Input
search_term = input("Enter the search term: ")
pages = input("Pages to scrape: ")
rs = open(search_term.replace(" ","_").lower()+'_jobs.txt', 'w')

#I like having a nice little title on my text document that gives me some info!
print("Scraped on: "+str(datetime.utcnow()))
rs.write("Scraped on: "+str(datetime.utcnow())+"\n")

#Initializing our iterator.
i=0

#Perform an infinite loop, let's scrape literally every relevant job.
while True:
    url = 'https://www.indeed.com/jobs?q='+search_term+"&start="+str(i)
    i+=10
    
#Some code that will prevent timeouts or retry errors by doing a bit of buffering and setting a max retries limit.
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url)
    
#Hello soup, you look beautiful today! Got any cards for me?
    soup = bs(r.content, 'html.parser')
    job_cards = soup.find_all('td', class_="resultContent")
    
    
#Let's look through the job cards on the search page.
    for job_card in job_cards:
        
#Use the Title element to find the href extension and the Job Title
        title = job_card.find('a',class_="jcs-JobTitle")
        unique_url="https://indeed.com"+title['href']
        unique_url.strip(" ")
        print(title.text,": ", end="")
        
#Search the job card for any listed payment, we will handle exceptions later
        pay = job_card.find(class_='metadata salary-snippet-container')
        
#Let's dig into the actual lsiting page and pull some Hiring Insights to inform our search
#We will reuse the session to avoid rewriting unecessary code
        listing_page_request = session.get(unique_url)
        listing_page = bs(listing_page_request.content,'html.parser')
        insights = listing_page.find_all('p', {'class' : re.compile('jobsearch-HiringInsights-entry.*')})
        
# set up some exceptions to handle formatting and reference errors to NoneTypes
        if pay is not None:
            print(pay.text)
            rs.write(title.text+": "+pay.text+"\n"+unique_url)
        else:
            print("No salary available")
            rs.write(title.text+": No salary available\n"+unique_url)
            
#There are multiple kinds of insights, and they are in a list. That means we have to set up an inner loop.
        for insight in insights:
            print(insight.text)
            rs.write("\n"+insight.text)
        
#I don't like having an extra line at the end so I threw a little conditional spice in!
        if job_cards[-1] is not job_card:
            print()
            rs.write("\n\n")
    print()
    
#Let's also make sure we're not beyond our known page limits
    print("Page #: "+str(int(i/10)))

#Not the cleanest way to kill the loop, but it works... for now. Definitely means there will be duplicates
    if int(i/10)==int(pages):
        break
#Get your resumes ready.        
rs.close()