from cgitb import html
from turtle import ht
from bs4 import BeautifulSoup
import requests
import pandas as pd

def parse_tables (tables):

    rows = []
    headers=[]
    reset_header=True
    rowspan = 1
    for table in tables:
        for child in table.children:
        
            column_index = 0
            
            for td in child:
                row = []
                try:
                    style = td.get('style')
                    colspan = int(td.get('colspan'))
                    content = td.text.replace('\n', '').strip()
                    if content == '':
                        continue
                    #content = content.text.replace('\n','')
                    if style == 'background-color: lightgray; vertical-align: top':
                        if reset_header:
                            headers = []
                            reset_header=False
                        #print ('HEADER')
                        i = 0
                    # print(colspan)
                        
                        while i < colspan:
                            headers.append(content)
                            i+=1
                    elif style == 'background-color: #dce6f2; vertical-align: top':
                        #print('SESSION')
                
                    
                        if colspan == 1:
                            #print (content)
                            #print (column_index)
                            #print(rowspan)
                            reset_header = True
                            if column_index == 0:
                                rowspan -= 1
                                column_index += rowspan
                                rowspan = int(td.get('rowspan'))  
                            #print (column_index)
                            header = headers[column_index]

                            #row.append(content)
                            row={"session": content, "category": header}


                        #row.append(header[column_index])
                            column_index+=1
                except:
                    continue
                
                #print (row)
                if len(row) > 0:
                    rows.append(row)
    #print (header)
    #print (rows[0])

    df = pd.DataFrame(rows)
    return df


url = "https://2022.pycon.de/schedule-full-table/"
#url = 'https://2022.pycon.de/scheduleT/'
#url='https://2022.pycon.de/program/'
r = requests.get(url)
html_doc = r.text

#with open("schedule.html", "a", encoding='utf8') as p:
#        p.write(html_doc)


soup = BeautifulSoup(html_doc,features="lxml")

trs = soup.select('tr[style*=";background-color:"]')

#print (soup.find_all('table'))

tables = soup.find_all('table')

df = parse_tables(tables)


print(df)

#print (soup.prettify())

tables = pd.read_html(url)

#print(tables[0][[1,2,3,4,5,6,7]])

#for tab in tables:
#    print(tab.head())

#for tab in tables:
#   print (tab[[1,2]].head())