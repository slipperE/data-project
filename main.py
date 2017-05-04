import dataLoader
import readTopics
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.sparse.csr import csr_matrix
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
import sys
from datetime import datetime
import csv

def PrintToSubmissionCSV(csvWriter, reportName, labelsInReport, allLabels):
    csvRow = [0] * len(allLabels)
    for label in labelsInReport:
        csvRow[allLabels.index(label)] = 1
    csvRow.insert(0, reportName)
    csvWriter.writerow(csvRow)

np.set_printoptions(threshold=np.nan)


load = dataLoader.loadData("trainingData", 'TrainingData')
reports = load.getAllReports()
topicDictionary = readTopics.readTopics()

myLabelMatrix = []
corpus = []
tf = TfidfVectorizer(input='content',
                     analyzer='word',
                     ngram_range=(1,3),
                     min_df = 0.00009,
                     max_features = 200000,
                     stop_words = 'english',
                     use_idf = True,
                     sublinear_tf=False)
print ('initial time')
initialTime = datetime.now()
print (initialTime)
for report in reports:
    reducedTopics = topicDictionary.generateMultiLabelArray(report.topics)
    if reducedTopics:
        myLabelMatrix.append(reducedTopics)
        corpus.append(report.bodyText)

print(myLabelMatrix)

print ('end of loop')
print (datetime.now() - initialTime )
tfidf_matrix = tf.fit_transform(corpus)

print('tfidf matrix made')
print (datetime.now() - initialTime )
mlb = MultiLabelBinarizer()
labeledTopics = mlb.fit_transform(myLabelMatrix)
print('created labeled topics')
print (datetime.now() - initialTime )
classifier = OneVsRestClassifier(SGDClassifier(n_jobs = 1)).fit(tfidf_matrix, labeledTopics)
print('done classification')

predictData = dataLoader.loadData("testData", 'TestData')
reportsToPredict = []
reportNames = []
for reportToPredict in predictData.getAllReports():
    reportsToPredict.append(reportToPredict.bodyText)
    reportNames.append(reportToPredict.documentName)

reportToPredictMatrix = tf.transform(reportsToPredict)
print('reportToPredictmatrix made')
print (datetime.now() - initialTime )

y_pred = classifier.predict(reportToPredictMatrix)
all_labels = mlb.inverse_transform(y_pred)

print (datetime.now() - initialTime )
print("check result!")

header = ['id'] + topicDictionary.lookupList
with open('Results/Submission.csv', 'w', newline='') as outcsv:
    csvWriter = csv.writer(outcsv)

    csvWriter.writerow(header)

    for reportName, labels in zip(reportNames, all_labels):
        PrintToSubmissionCSV(csvWriter,
                             reportName,
                             labels,
                             topicDictionary.lookupList)
print('Completed')
print (datetime.now() - initialTime )
