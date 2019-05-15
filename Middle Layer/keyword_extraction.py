# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 15:46:16 2019

@author: welcome

Extracting keywords from the Questions
"""

import pandas as pd
import openpyxl
from rake_nltk import Rake
import re

wb = openpyxl.load_workbook('output1.xlsx')
ws =  wb['Sheet1']

count = 0
questions = []
for row in ws.iter_rows():
    if count == 0:
        count += 1
        continue
    cell = row[0]
    questions.append(cell.value)
    count += 1

keywords = []
for text in questions:
    r = Rake()
    r.extract_keywords_from_text(text)
    words = r.get_ranked_phrases()
    ans = []
    for string in words:
        str_word = []
        for word in string.split():
            if re.match("^[a-z0-9_-]*$", word):
                str_word.append(word)
        words = ' '.join(str_word)
        ans.append(words)
    keywords.append(ans)

d = {'Question':questions, 'Keywords':keywords}
df = pd.DataFrame(d)
df.to_csv('Keywords.csv')

#df = pd.read_csv('output1.xlsx')
#print(df.head())