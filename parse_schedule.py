from cgitb import html
from turtle import ht
from bs4 import BeautifulSoup
import requests
import pandas as pd

def parse_tables (tables):
    """
    Parses the tables from the PyConDe 2022 schedule. 

    This function loops through the PyConDe 2022 schedule web page.
    Does make multiple assumptions about the expected structure (like color usage, rowspans and colspans) 
    in order to get the right elements.

    Parameters
    ----------
    tables : BeautifulSoup ResultSet
        ResultSet containing the table elements

    Returns
    -------
    DataFrame
        DataFrame with columns ``session`` and ``category``
        
    """

    # initialize variables
    rows = []
    headers=[]
    reset_header=True
    rowspan = 1

    for table in tables:
        for child in table.children:
            
            # reset the column index once we start a new row in the table
            column_index = 0
            
            for td in child:
                # reset the row data once we start a new column
                row = []
                try:
                    # get style to distinguish header and content
                    style = td.get('style')
                    # get colspan to recognize non-session lines, like coffee or lunch breaks
                    colspan = int(td.get('colspan'))
                    # read column content, but drop newlines and whitespace
                    content = td.text.replace('\n', '').strip()
                    # if content is empty, skip column
                    if content == '':
                        continue
                    # if background color is lightgray, current cell is header
                    if style == 'background-color: lightgray; vertical-align: top':
                        # if this is the first cell of a new header, reset header data
                        if reset_header:
                            headers = []
                            reset_header=False
                        
                        i = 0
                        # if header spans multiple columns, create multiple headers                        
                        while i < colspan:
                            headers.append(content)
                            i+=1
                    # if background color is blue-ish, current cell is potential session data
                    elif style == 'background-color: #dce6f2; vertical-align: top':           
                        # non-session cells like coffee breaks have colspan > 1
                        if colspan == 1:
                            # once we encounter a session, the next header we detect should reset header data
                            reset_header = True
                            # check if column is first column in row
                            if column_index == 0:
                                # rowspan will have value of the first column of previous row,
                                # or 1 if this is the first row.
                                # this is significant if the previous first column had rowspan = 2.
                                # in that case, all column headers shift one to the right.
                                rowspan -= 1
                                column_index += rowspan
                                rowspan = int(td.get('rowspan'))  
                            
                            # locate the right header for the current cell
                            header = headers[column_index]
                            # create row with two columns, one for the session and one for the category
                            row={"session": content, "category": header}
                            # increase column_index to move header one to the right
                            column_index+=1
                except:
                    continue
                # if row contains data, add to the list
                if len(row) > 0:
                    rows.append(row)
    # create dataframe based on the rows
    df = pd.DataFrame(rows)
    # return dataframe
    return df

# url of the PyConDe 2022 schedule in table format.
url = "https://2022.pycon.de/schedule-full-table/"
# get the request data
r = requests.get(url)
html_doc = r.text

# save html to file, in case the website goes down. only needed once.
#with open("schedule.html", "a", encoding='utf8') as p:
#        p.write(html_doc)

# parse the response in BeautifulSoup
soup = BeautifulSoup(html_doc,features="lxml")
# find all table elements in response
tables = soup.find_all('table')
# convert html tables into dataframe
df = parse_tables(tables)


print(df)