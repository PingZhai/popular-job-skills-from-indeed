from bs4 import BeautifulSoup # For HTML parsing
import re # Regular expressions
from time import sleep # To prevent overwhelming the server between connections
import pandas as pd # For converting results to a dataframe and bar chart plots
from nltk.corpus import stopwords # Filter out stopwords, such as 'the', 'or', 'and'
from collections import Counter # Keep track of our term counts
import requests
import urllib2 # Website connections
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np
def text_cleaner(website):
    r = requests.get(website)
    soup_obj = BeautifulSoup(r.content, "html.parser")  
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    
    text = soup_obj.get_text() # Get the text from this
    lines = (line.strip() for line in text.splitlines()) # break into lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    
    def chunk_space(chunk):
        chunk_out = chunk + ' ' # Need to fix spacing issue
        return chunk_out              
    text = ''.join(chunk_space(chunk) for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line                
    # Now clean out all of the unicode junk (this line works great!!!)
        
    try:
        text = text.decode('unicode_escape').encode('ascii', 'ignore') # Need this as some websites aren't formatted
    except:                                                            # in a way that this works, can occasionally throw
        return                                                         # an exception
               
    text = re.sub("[^a-zA-Z.+3]"," ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)      
    text = text.lower().split()  # Go to lower case and split them apart
    stop_words = set(stopwords.words("english")) # Filter out any stop words
    text = [w for w in text if not w in stop_words]      
    text = list(set(text)) # Last, just get the set of these. Ignore counts (we are just looking at whether a term existed
                            # or not on the website)        
    return text



#test data scientist jobs

city = "Raleigh" 
state = "NC"    
         
final_job = 'data+scientist' # searching for data scientist exact fit("data scientist" on Indeed search)
    
if city is not None:
    final_city = city.split() 
    final_city = '+'.join(word for word in final_city)
    final_site_list = ['http://www.indeed.com/jobs?q=%22', final_job, '%22&l=', final_city,
                    '%2C+', state] # Join all of our strings together so that indeed will search correctly
else:
    final_site_list = ['http://www.indeed.com/jobs?q="', final_job, '"']

final_site = ''.join(final_site_list) # Merge the html address together into one string

base_url = 'http://www.indeed.com'
    
print final_site
    
try:
    html = urllib2.urlopen(final_site).read() # Open up the front page of our search first
except:
        'That city/state combination did not have any jobs. Exiting . . .' # In case the city is invalid
        
soup = BeautifulSoup(html,'lxml') # Get the html from the first page
num_jobs_area = soup.find(id = 'searchCount').string.encode('utf-8') # Now extract the total number of jobs found
job_numbers = re.findall('\d+', num_jobs_area) # Extract the total jobs found from the search result
if len(job_numbers) > 2: # Have a total number of jobs greater than 1000
    total_num_jobs = (int(job_numbers[1])*1000) + int(job_numbers[2])
else:
    total_num_jobs = int(job_numbers[1]) 
city_title = city
if city is None:
    city_title = 'Nationwide'
            
num_pages = total_num_jobs/10 # This will be how we know the number of times we need to iterate over each new
                                      # search result page
job_descriptions = [] # Store all our descriptions in this list
    
for i in xrange(1,num_pages+1): # Loop through all of our search result pages
    print 'Getting page', i
    start_num = str((i-1)*10) # Assign the multiplier of 10 to view the pages we want
    current_page = ''.join([final_site, '&start=', start_num])
        # Now that we can view the correct 10 job returns, start collecting the text samples from each
    r = requests.get(current_page)
    soup = BeautifulSoup(r.content, "html.parser")  
    tbl = soup.find(id="resultsCol")
        
    for link in tbl.find_all('a'):
        if link.has_attr('href') and "fccid" in link.attrs['href'] and "salaries" not in link.attrs['href']:
            url = link.attrs['href']
            final_description = text_cleaner("http://www.indeed.com"+url)
            if final_description: 
                job_descriptions.append(final_description)
            sleep(1) 
                
doc_frequency = Counter() 
[doc_frequency.update(item) for item in job_descriptions] 
language_name=np.array(['R','Python','Java','C++','Ruby','Perl','Matlab','JavaScript','Scala','Fortran'])

language_count = np.zeros(language_name.size)
for n in range(0,language_name.size):
    language_count[n]=Counter({language_name[n]:doc_frequency[language_name[n].lower()]})[language_name[n]]




x = np.arange(language_name.size)

#get median income and median house price 
data = pd.read_csv("Sale_Prices_City.csv")
[ncity,nterm]=data.shape
CITY='New York'
STATE='New York'

for n in range(0,ncity):
    cityname= data.loc[n][1]
    statename=data.loc[n][2]
    if ((cityname == CITY) & (statename == STATE)):
        break

price=int(np.nanmean(data.loc[n][-12:])/1000.)

data = pd.read_csv("Affordability_Income_2017Q3.csv")
[ncity,nterm]=data.shape
CITY='New York, NY'

for n in range(0,ncity):
    cityname= data.loc[n][1]
    if (cityname == CITY):
        break

income=int(np.nanmean(data.loc[n][-12:])/1000.)
print price,income

fig = plt.figure(1,figsize=(9, 4))
ax = plt.gca()
#ax.yaxis.set_major_formatter(formatter)
plt.bar(x, 100.0*language_count[indextmp]/total_num_jobs)
plt.xticks(x, (language_name[indextmp]),fontsize=14)
plt.xticks(fontsize = 14,rotation=30)
plt.yticks(fontsize = 14)
ax.set_ylabel('Percentage in Job Ads', color='k',fontsize=14)
ax.set_title('data scientist skills in '+city+", "+state,fontsize = 18)

ax.annotate('Job Numbers: '+str(total_num_jobs), (0.4, 0.8), textcoords='axes fraction', size=16)
ax.annotate('Median Family Income: $'+str(income)+'K', (0.4, 0.7), textcoords='axes fraction', size=16)
ax.annotate('Median House Price: $'+str(price)+'K', (0.4, 0.6), textcoords='axes fraction', size=16)
plt.tight_layout()
plt.savefig("data scientist jobs in "+city+state+".png")
plt.show()


