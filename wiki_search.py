import re
from Stemmer import Stemmer
from collections import defaultdict
import sys
import os
import math
import time

dictIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
titles = defaultdict(str)
tempDict = defaultdict(int)
ps = Stemmer("porter")
firstLineIndex = []
firstLineTitle = []
TOTALDOCS = 0
titleOffset = 10000

def readIndexAndTitle():
	global TOTALDOCS,titleOffset
	## Read Title File into titles Dictionary
	indexFileNumber = 3
	while(1):
		if not os.path.exists("index/"+str(indexFileNumber)+".txt"):
			break
		currentFile = open("index/"+str(indexFileNumber)+".txt",'r')
		firstLine = currentFile.readline().strip('\n')
		currentFile.close()
		#print(firstLine.split("|")[0])
		firstLineIndex.append(firstLine.split("|")[0])
		indexFileNumber+=1

	titleFileNumber = 1
	while(1):
		if not os.path.exists("title/"+str(titleFileNumber)+".txt"):
			break
		currentFile = open("title/"+str(titleFileNumber)+".txt",'r')
		firstLine = currentFile.readline().strip('\n')
		currentFile.close()
		#print(firstLine.split(":")[0])
		firstLineTitle.append(firstLine.split(":")[0])
		titleFileNumber+=1
		TOTALDOCS += titleOffset



def simpleQuery(query):
	global TOTALDOCS
	ti = time.time()
	print("---------",query,"---------")
	tempDict.clear()	
	x = []
	y = []
	number = query.split(",")
	qry = number[1]
	words = qry.split(" ")
	for word in words:
		#print(word,":")
		if(word == " " or word ==""):
			continue
		word = word.lower()
		word = ps.stemWord(word)
		#print(word)
		fileNumber = firstLineIndex.index(max(i for i in firstLineIndex if i<=word))
		fileNumber += 3
		file = open("index/"+str(fileNumber)+".txt")
		line = file.readline().strip("\n")
		wordFoundExact = 0
		while(line):
			wordDetail = line.split("|")
			wordFromIndex = wordDetail[0]
			detail = wordDetail[1]
			if(word == wordFromIndex):
				wordFoundExact = 1
				break
			line = file.readline().strip("\n")
		file.close()
		#print(fileNumber)
		if(fileNumber==0):
			continue
		Id =[]
		idDescription = []
		details = detail.split("+")
		documentFrequency = 0
		for values in details:
			if(values == "" or values == " "):
				continue
			idandDetail = values.split(":")
			ID = idandDetail[0]
			if(ID == "" or ID == " " or ID == "\n"):
				continue
			Id.append(ID)
			description = idandDetail[1].strip("+")
			description = description.split(",")
			count = 0
			weightage = 0
			for quant in description:
				try:
					freq = quant[1:]
					tg = quant[0]
				except:
					pass
				if len(freq) and freq.isdigit():
					if(tg == "T"):
						weightage += .25
					elif (tg == "B"):
						weightage += .25
					elif (tg == "I"):
						weightage += .15
					else:
						weightage += .1
					count += int(freq) 
			
			documentFrequency += 1
			tempDict[ID] += (math.log10(1+int(count))*math.log10(TOTALDOCS/(len(details)+1))*weightage)
		#print(len(details))

	for key,val in tempDict.items():
		x.append(key)
		y.append(val)
	outputFile= open("./20171078_queries_op.txt","a")
	k = int(number[0])
	z = [x1 for _,x1 in sorted(zip(y,x))]
	z.reverse()
	#print(z)
	printed = 0
	for ansId in z:
		if printed >= k:
			break
		idx = ansId
		indexTitle = float(int(idx)/titleOffset)
		indexTitle = int(indexTitle)+1
		file = open("title/"+str(indexTitle)+".txt","r")
		line = file.readline().strip('\n')
		name = "----"
		while line:
			words = line.split(':')
			firstword = words[0]
			name = words[1]
			for leg in range(2,len(words)):
				name += ":"+words[leg]
			if firstword == idx:
				break
			line = file.readline().strip('\n')
		file.close()
		#print(name)
		if(len(words)>2):
			continue
		printed += 1
		outputFile.write(ansId)
		outputFile.write(",")
		outputFile.write(name)	
		outputFile.write("\n")
	
	a = time.time()-ti
	outputFile.write(str(a))
	# outputFile.write(", ")
	# outputFile.write(str(a/k))
	outputFile.write("\n")
	outputFile.write("\n")
	outputFile.close()
		
def fieldQueries(query):
	ti = time.time()
	print("---------",query,"---------")
	tempDict.clear()	
	x = []
	y = []
	fields = ['']
	number = query.split(",")
	qry = number[1]
	words = re.split(r'[tbicrl][:]',qry)
	for i in range (len(query)):
		if query[i] == ":":
			fields.append(query[i-1])
	#print(fields)
	#print(words)
	for i in range (1,len(fields)):
		if(1):
			fieldquery=fields[i]
			wordquery=words[i]
			#print (fieldquery,wordquery)
			queriesWord = wordquery.split(" ")
			#print(queriesWord)
			for word in queriesWord:
				if(len(word)<2):
					continue
				#print(word,":")
				word = word.lower()
				word = str(ps.stemWord(word))
				fileNumber = firstLineIndex.index(max(i for i in firstLineIndex if i<=word))
				fileNumber += 3
				file = open("index/"+str(fileNumber)+".txt")
				line = file.readline().strip("\n")
				wordFoundExact = 0
				while(line):
					wordDetail = line.split("|")
					wordFromIndex = wordDetail[0]
					detail = wordDetail[1]
					if(word == wordFromIndex):
						wordFoundExact = 1
						break
					line = file.readline().strip("\n")
				file.close()
				if(fileNumber==0):
					continue
				Id =[]
				idDescription = []
				counts = []
				matchedDocuments = 0
				details = detail.split("+")
				documentFrequency = 0
				for values in details:
					if(values == "" or values == " "):
						continue
					idandDetail = values.split(":")
					ID = idandDetail[0]
					if(ID == "" or ID == " " or ID == "\n"):
						continue
					Id.append(ID)
					description = idandDetail[1].strip("+")
					description = description.split(",")
					count = 0
					weightage = 0
					for quant in description:
						try:
							freq = quant[1:]
							tg = quant[0]
						except:
							pass
						if len(freq) and freq.isdigit():
							if(tg.lower() == fieldquery):
								#print(ID)
								count += int(freq)
								matchedDocuments+=1
					counts.append(count)
				
				if(fieldquery == "t"):
					weightage += .25
				elif (fieldquery == "b"):
					weightage += .25
				elif (fieldquery == "i"):
					weightage += .15
				else:
					weightage += .1

				for j in range(len(Id)):
					if(counts[j]!=0):
						tempDict[Id[j]] += (math.log10(1+int(counts[j]))*math.log10(TOTALDOCS/(matchedDocuments+1))*weightage)

	for key,val in tempDict.items():
		x.append(key)
		y.append(val)
	#PrintResults(x,y,int(number[0]),ti)
	outputFile= open("./20171078_queries_op.txt","a")
	k = int(number[0])
	z = [x1 for _,x1 in sorted(zip(y,x))]
	z.reverse()
	#print(z)
	printed = 0
	for ansId in z:
		if printed >= k:
			break
		idx = str(int(ansId))
		indexTitle = float(int(idx)/titleOffset)
		indexTitle = int(indexTitle)+1
		file = open("title/"+str(indexTitle)+".txt","r")
		line = file.readline().strip('\n')
		name = "----"
		while line:
			words = line.split(':')
			firstword = words[0]
			name = words[1]
			for leg in range(2,len(words)):
				name += ":"+words[leg]
			name = name.strip(":")
			if firstword == idx:
				break
			line = file.readline().strip('\n')
		file.close()
		#print(name)
		if(len(words)>2):
			continue
		printed += 1
		outputFile.write(ansId)
		outputFile.write(",")
		outputFile.write(name)	
		outputFile.write("\n")
	
	a = time.time()-ti
	outputFile.write(str(a))
	# outputFile.write(", ")
	# outputFile.write(str(a/k))
	outputFile.write("\n")
	outputFile.write("\n")
	outputFile.close()

def search(queries):
	f = open("./20171078_queries_op.txt","w")
	f.write("")
	f.close()

	for query in queries:
		if query == '' or len(query)<2:
			continue
		querySplit = query.split("\n")
		for words in querySplit:
			if len(words) ==0:
				continue
			if ':' in words:
				fieldQueries(words)
			else:
				simpleQuery(words)

def readQuery(testFile):
	with open(testFile, 'r') as file:
		queries = file.readlines()
	return queries

if __name__ == '__main__':
	readIndexAndTitle()
	#print(TOTALDOCS)
	queries = readQuery("./20171078_queries1.txt")
	#print(queries)
	search(queries)
	print("Done")
