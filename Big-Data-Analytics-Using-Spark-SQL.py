# -*- coding: utf-8 -*-
"""BDA Assignment 2 Alishba.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M3JOxXqgILOOyB6t2zFPQVf_kqviTDMY
"""

print("Bismillah")

"""# **Installations**"""

!pip install pyspark
!pip install -U -q PyDrive
!apt install openjdk-8-jdk-headless -qq
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# Let's import the libraries we will need
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import pyspark
from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark import SparkContext, SparkConf

# # Import and create a new SQLContext 
# from pyspark.sql import SQLContext

# create the session
conf = SparkConf().set("spark.ui.port", "4050")

# create the context
sc = pyspark.SparkContext(conf=conf)
spark = SparkSession.builder.getOrCreate()
sqlContext = SQLContext(sc)

"""# **Pre-Processing**"""

# Read the country CSV file into an RDD.
country_lines = spark.read.csv('/content/drive/MyDrive/BDA/Assignment02/country-list.csv', sep = ',',  inferSchema = True)
country_lines = country_lines.selectExpr("_c0 as Country", "_c1 as Code")
country_lines.show()
country_lines.printSchema()
type(country_lines)
country_lines.count()

country_lines.take(3)

# Convert each line into a pair of words

# Convert each pair of words into a tuple

# Create the DataFrame, look at schema and contents
# countryDF = sqlContext.createDataFrame(country_tuples, ["country", "code"])
# countryDF.printSchema()
# countryDF.take(3)

country_lines.count()

# Read tweets JSON file
users = spark.read.json("/content/drive/MyDrive/BDA/Assignment02/users.json")
users.show()
users.printSchema()

users.columns

users.count()

users.select("tweet_text").show()

# Clean the data: some tweets are empty. Remove the empty tweets using filter() 
users = users.filter(users.tweet_text.isNotNull())
users.count()

import re

def ascii_ignore(x):
  x = x.encode('ascii', 'ignore').decode('ascii')
  # x = re.sub(r'\W+', ' ', x)
  x = re.sub(r'[^a-zA-Z0-9]', ' ', x)
  # x.replace('[^a-zA-Z]', '')
  return x

ascii_udf = udf(ascii_ignore)

clean_users = users.withColumn("clean_tweet_text", ascii_udf('tweet_text'))
clean_users.show()
clean_users.count()

# Perform WordCount on the cleaned tweet texts. (note: this is several lines.)
lines = clean_users.select("clean_tweet_text").rdd.flatMap(lambda x:x)
lines.show()

words = lines.flatMap(lambda line : line.split(" "))

tuples = words.map(lambda word: (word , 1))

counts = tuples.reduceByKey(lambda a , b: (a + b))

type(counts)

type(counts.collect())

counts.take(3)

counts.count()

# Create the DataFrame of tweet word counts
WordCount = spark.createDataFrame(counts, ["Words", "Count"])
WordCount.show()
WordCount.count()

CountryDF = country_lines.selectExpr("Country as Words")
 CountryDF.show()

# Join the country and tweet DataFrames (on the appropriate column)
MyPyaraTable = WordCount.join(CountryDF, on = ["Words"], how = 'inner') # I joined with Country only because Codes did not exist in tweet texts
MyPyaraTable.show()
MyPyaraTable.count()

MyPyaraTable.registerTempTable("PyaraTable")

"""# **Question 1.1:  how many different countries are mentioned in the tweets**"""

# Question 1: number of distinct countries mentioned
MyPyaraTable.count()

# Also By SQL Query
Counting = spark.sql("""Select Count(*) AS Count_Mention From PyaraTable""")
Counting.show()

"""# **Question 1.2:   computes the total number of times any country is mentioned**"""

# Question 2: number of countries mentioned in tweets.
from pyspark.sql.functions import sum
# MyPyaraTable.printSchema()
MyPyaraTable.groupBy().sum().show()

# Also By SQL Query
CountriesMentioned = spark.sql("""Select Sum(Count) AS Sum_Mention From PyaraTable""")
CountriesMentioned.show()

"""# **Question 1.3:   Your next task is to determine the most popular countries. You can do this by finding the three countries mentioned the most.**"""

# Table 1: top three countries and their counts.
from pyspark.sql.functions import desc

# MyPyaraTable.sort(desc("Count")).show(truncate = 3) #Something Cool
# MyPyaraTable.sort(desc("Count")).take(3) #Another Way to accomplish it
MyPyaraTable.sort(desc("Count")).show(3)

# Also By SQL Query
DesccendingOrder = spark.sql("""SELECT * FROM PyaraTable ORDER BY Count Desc LIMIT 3;""")
DesccendingOrder.show()

"""# **Question 1.4:  you are now interested in how many times specific countries are mentioned. For example, how many times was France mentioned?**"""

MyPyaraTable.where(MyPyaraTable.Words == 'France').show()

# Also By SQL Query
WhereFrance = spark.sql("""SELECT * FROM PyaraTable WHERE Words = 'France';""")
WhereFrance.show()

"""# **Question 1.5:   Which country has the most mentions: Kenya, Wales, or Netherlands?**"""

MyPyaraTable.where( (MyPyaraTable.Words == 'Kenya') | (MyPyaraTable.Words == 'Wales') | (MyPyaraTable.Words == 'Netherlands') ).sort(desc("Count")).show(1)

# Also By SQL Query
TopAmong3 = spark.sql("""SELECT * FROM PyaraTable WHERE Words = 'Kenya' OR Words = 'Wales' OR Words = 'Netherlands' ORDER BY 2 DESC LIMIT 1 ;""")
TopAmong3.show()

"""# **Question 2.6:   Finally, what is the average number of times a country is mentioned?**"""

# MyPyaraTable.groupBy().avg("Count").show() #Also possible
MyPyaraTable.groupBy().agg(avg("Count").alias("Average Number of Country Mentioned")).show()

# Also By SQL Query
AverageMention = spark.sql("""SELECT AVG(Count) AS Country_Avg_Mention FROM PyaraTable ;""")
AverageMention.show()

# A good line of code we should know
# df.filter(df.location.contains('google.com'))

# Table 2: counts for Wales, Iceland, and Japan.

"""# **Link for Colab Python Notebook: https://colab.research.google.com/drive/1M3JOxXqgILOOyB6t2zFPQVf_kqviTDMY?usp=sharing**"""