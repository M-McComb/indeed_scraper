#This is a first try at web scraping in python
#It requires the bs4 and requests libraries
#Note that this program will only scrape the first page of Indeed
import re
import requests as rqs
from bs4 import BeautifulSoup as bs

search_term = input("Enter the search term: ")
rs = open(search_term.replace(" ","_").lower()+'_jobs.txt', 'w')
url = 'https://www.indeed.com/jobs?q='+search_term+'&l='
r = rqs.get(url)

soup = bs(r.content, 'html.parser')
job_cards = soup.find_all('td', class_="resultContent")
for job_card in job_cards:
    title = job_card.find('a',class_="jcs-JobTitle")
    
    unique_url="https://indeed.com"+title['href']
    unique_url.strip(" ")
    print(title.text,": ", end="")
    
    pay = job_card.find(class_='metadata salary-snippet-container')
    
    listing_page_request = rqs.get(unique_url)
    listing_page = bs(listing_page_request.content,'html.parser')
    insights = listing_page.find_all('p', {'class' : re.compile('jobsearch-HiringInsights-entry.*')})
    
    if pay is not None:
        print(pay.text)
        rs.write(title.text+": "+pay.text+"\n"+unique_url)
    else:
        print("No salary available")
        rs.write(title.text+": No salary available\n"+unique_url)
    for insight in insights:
        print(insight.text)
        rs.write("\n"+insight.text)
    if job_cards[-1] is not job_card:
        print()
        rs.write("\n\n")
rs.close()