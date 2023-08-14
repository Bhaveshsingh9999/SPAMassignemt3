# -*- coding: utf-8 -*-
"""emailclassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sER0gl5lJBwPvUnCmEB_T152kdikHXfG
"""

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
data = pd.read_csv("spam_ham_dataset.csv")
dictionary={}
test_mails=[]

# Function that reads and appends the data of each text file in the test folder into a list
def read_text_file(file_path):
  global test_mails
  with open(file_path, 'r') as f:
      test_mails.append([f.read()])

#code for testing using the test folder
import os
import csv

#keep a tab of current path 
currentpath=os.getcwd()
old_path=currentpath
#to store the emails from the folder this will be stored as list of list 
test_mails=[]
#changing the path to go in side test folder 
currentpath=currentpath+"/test"
os.chdir(currentpath)
# Calling the read_text_file function for all .txt files in folder test 
for file in os.listdir():
    if file.endswith(".txt"):
        file_path = f"{currentpath}/{file}"
        read_text_file(file_path)

# Back to old path outside test folder to have the final result csv in ths path 
os.chdir(old_path)

def cleaningdata():
  #the list is taken from nltk.corpus
  listofstopwords=[" ourselves "," re ","subject ", " hers " , " between " , " yourself " , " but " , " again " , " there " , " about " , " once " , " during " , " out " , " very " , " having " , " with " , " they " , " own " , " an " , " be " , " some " , " for " , " do " , " its " , " yours " , " such " , " into " , " of " , " most " , " itself " , " other " , " off " , " is " , " s " , " am " , " or " , " who " , " as " , " from " , " him " , " each " , " the " , " themselves " , " until " , " below " , " are " , " we " , " these " , " your " , " his " , " through " , " don " , " nor " , " me " , " were " , " her " , " more " , " himself " , " this " , " down " , " should " , " our " , " their " , " while " , " above " , " both " , " up " , " to " , " ours " , " had " , " she " , " all " , " no " , " when " , " at " , " any " , " before " , " them " , " same " , " and " , " been " , " have " , " in " , " will " , " on " , " does " , " yourselves " , " then " , " that " , " because " , " what " , " over " , " why " , " so " , " can " , " did " , " not " , " now " , " under " , " he " , " you " , " herself " , " has " , " just " , " where " , " too " , " only " , " myself " , " which " , " those " , " i " , " after " , " few " , " whom " , " t " , " being " , " if " , " theirs " , " my " , " against " , " a " , " by " , " doing " , " it " , " how " , " further " , " was " , " here " , " than " ]
  data['text']=data['text'].str.lower()
  #data cleaning
  data['text']= data['text'].str.replace(r"[^a-zA-Z\d\' ']+", " ") # removing unwanted special symbol like #,/,(),@ that does not add any value to the classifier
  for i in listofstopwords:                                        # to remove the stop words 
    data['text'] = data['text'].str.replace(i,' ')    
  data['text']= data['text'].str.replace("'", " ")
  data['text']= data['text'].str.replace(' +',' ')    #to remove mutiple space

def dictmaking():
  count=0
  for i in range(data.shape[0]):
    text=data.iloc[i,2].split()
    for j in text:
      if j not in dictionary:
        dictionary[j]=count
        count =count+1

def dictcount():
  dcount={}
  for i in range(data.shape[0]):
    text=data.iloc[i,2].split()
    for j in text:
      if j not in dcount:
        dcount[j]=1
      else:
        dcount[j]+=1
  return dcount

#remove the words having very low frequency or taking the top words 
def listofwords(x,sorted_dcount):
  finaldict={}
  count=0
  for i in sorted_dcount:
    finaldict[i]=count
    count+=1
    if count==x :
      break
  return finaldict

# seprate spam and nonspamdata
def seprate(X):
  
  nonspam = X[X['label_num'] == 0]
  spam = X[X['label_num'] == 1]
  return (nonspam,spam)

#to convert the text mail into 1 0 vector 
def convertfunc(X,lwords):
  countmatrix=np.zeros((X.shape[0],len(lwords)))
  result=np.zeros((X.shape[0]))

  for i in range(X.shape[0]):
    text = X.iloc[i,2].split()
    for words in text:
      if words in lwords:
        countmatrix[i,lwords[words]]=1
        result[i]=X.iloc[i,3]

  return(countmatrix,result)

import operator
spamprob={}
nonspamprob={}

def maincall():
  global scount
  global nscount
  global lwords
  cleaningdata()
  dictmaking()   # getting all the words in dictionary 
  dcount=dictcount()  # getting a count on all the words to know there frequency
  sorted_dcount = dict( sorted(dcount.items(), key=operator.itemgetter(1),reverse=True))
  lwords=listofwords(18000,sorted_dcount)    # pass the no of words you need in dictionary and the sorted dictionary we get the final dictionary
  nonspam,spam=seprate(data)                 # to seprate the spam and nonspam dataset
  Xnonspam,Ynonspam=convertfunc(nonspam,lwords)  # this is to convert the nonspam message to vector
  Xspam,Yspam=convertfunc(spam,lwords)          # this is to convert the spam message in to vector
  #need to add a vector of all 1 in spam and non spam 
  Ynonspam=np.append(Ynonspam,0)
  Yspam=np.append(Yspam,1)
  b=np.ones(len(lwords))
  Xnonspam=np.append(Xnonspam,[b],axis=0)
  Xspam=np.append(Xspam,[b],axis=0)

  spamproblist=np.mean(Xspam,axis=0) 
  nonspamproblist=np.mean(Xnonspam,axis=0)

  nscount=Ynonspam.size
  scount=Yspam.size
  for i in range(len(spamproblist)):
    spamprob[i]=spamproblist[i]
  for i in range(len(nonspamproblist)):
    nonspamprob[i]=nonspamproblist[i]

# now to perform testing 
def testing(Xtest,lwords,spamcount,nonspamcount):
  Xtest=' '.join([str(elem)for elem in Xtest])  # to convert it to string 
  textdata=' '.join(dict.fromkeys(Xtest.split()))   # remove duplicated
  val=1
  listtextdata=textdata.split()
  Phat=spamcount/(spamcount+nonspamcount)
  for word in lwords:
    index=lwords[word]   # get the index of the word so to see the probability
    if word in listtextdata:
      p1=spamprob[index]
      p0=nonspamprob[index]
      val=val*p1/p0
    else:
      p1=1-spamprob[index]
      p0=1-nonspamprob[index]
      val=val*p1/p0
  val=np.log(val*(Phat/(1-Phat)))
  if val>0:
    return 1
  else:
    return 0

maincall()  # to train our model Naive bayes

# to do the testing ,after this the final result a csv will be produced in the current working directory consisting of the mail and 
#the corresponding result of spam(1) or no spam(0) 
num=len(test_mails)
final_label=[]
for i in range(num):
  testres=testing(test_mails[i],lwords, scount,nscount)
  print(testres)
  final_label.append([test_mails[i],testres])

file_name = "test_result.csv"

with open(file_name,'w') as csvfile:
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerow(['emails','label'])
    csvwriter.writerows(final_label)