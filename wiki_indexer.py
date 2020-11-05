import os
import re
import sys
import time
import xml.sax
from os import walk
from shutil import copyfile
from Stemmer import Stemmer
from collections import defaultdict
from nltk.corpus import stopwords as nltk_stopwords


infoBoxRegex = "\{\{Infobox ((.*?\n)*?) *?\}\}"
categoryRegex = "\[ *\[ *[cC]ategory *: *(.*?) *\] *\]"
referenceRegex = "== *[Rr]eferences *==((.*?\n)*?)\n"
#referenceRegex = "== *[Rr]eferences *==\n(((.*?\n)*?)\n)*=+?"
externalLinksRegex = "== *[eE]xternal [lL]inks *==\n((.*?\n)*?)\n"
externalLinksRegex = "== *[eE]xternal [lL]inks *==\n(((.*?\n)*?)\n) *?\{+?"


stemmer = Stemmer("porter")
stopWords = nltk_stopwords.words('english')
stopwords = defaultdict(int)
uniqueTokens = defaultdict(int)
dumpTokensCount = 0
documentsProcessed = 1
tempIndexFile = 1
documentLimit = 10000
noOfFile = 0

def stopwordDictForm():
	for word in stopWords: 
		word = stemmer.stemWord(word)
		if word :
			stopwords[word] = 1


def tokiz(content):
	tokens = re.split(r'[^A-Za-z0-9]+', content)
	return tokens


class XMLWikiHandler(xml.sax.ContentHandler):

	CurrentlyProcessing = 0

	def __init__(self):
		self.isIdDone = 0
		self.CurrentData = ""
		self.DocumentCount = 0
		self.dictIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
		self.titles = defaultdict(str)
		self.isword = defaultdict(int)
		self.networds = []


	def startElement(self,tag,attributes):
		global documentsProcessed
		global tempIndexFile
		global documentLimit
		self.CurrentData = tag
		if tag == "id" and XMLWikiHandler.CurrentlyProcessing==0:
			self.isIdDone = 1
			self.DocumentCount = documentsProcessed
			self.ID = ""
			XMLWikiHandler.CurrentlyProcessing = 1
			documentsProcessed += 1
			if(documentsProcessed%documentLimit==0):
				#documentsProcessed = 1
				self.writeFile(tempIndexFile)
				self.dictIndex.clear()
				self.isword.clear()
				self.titles.clear()
				self.networds.clear()
				tempIndexFile += 1

		elif tag == "title":
			self.Title = ""
		elif tag == "text":
			self.Text = ""


	def endElement(self,tag):
		global tempIndexFile

		if(self.CurrentData == "id" and XMLWikiHandler.CurrentlyProcessing == 1 and self.isIdDone == 1):
			self.isIdDone = 0
			#print("ID : ",self.DocumentCount)

		elif(self.CurrentData == "title"):
			#print("title : ",self.Title)
			self.titles[str(self.DocumentCount+1)] = self.Title
			
			dataTokens = tokiz(str(self.Title))
			#dumpTokensCount += len(dataTokens)
			for word in dataTokens:
				word = str(word).lower()
				if(stopwords[word]):
					continue
				stemmedword = stemmer.stemWord(word)
				if stemmedword.isdigit()==0 or (stemmedword.isdigit()==1 and len(stemmedword)<5):
					if not self.isword[stemmedword]:
						self.isword[stemmedword] = 1
						self.networds.append(stemmedword)
					self.dictIndex[stemmedword][str(self.DocumentCount+1)]["T"] +=1

		elif(self.CurrentData == "text"):
			content = self.Text
			externalLinks = re.findall(externalLinksRegex,content)
			category = re.findall(categoryRegex,content)
			references = re.findall(referenceRegex,content)
			infobox = re.findall(infoBoxRegex,content)
			self.enterToDict(infobox,"I",self.DocumentCount)
			self.enterToDict(category,"C",self.DocumentCount)
			self.enterToDict(references,"R",self.DocumentCount)
			self.enterToDict(externalLinks,"E",self.DocumentCount)

			contentNoLinks = re.sub(externalLinksRegex,'',content)
			contentNoCategory = re.sub(categoryRegex,'',contentNoLinks)
			contentNoReferences = re.sub(referenceRegex,'',contentNoCategory)
			contentNoInfobox = re.sub(infoBoxRegex,'',contentNoReferences)
			body = re.sub(r'\{\{.*\}\}','', contentNoInfobox)
			text_tokens = tokiz(body)
			for word in text_tokens:
				word = str(word).lower()
				if(stopwords[word]):
					continue
				stemmedword = stemmer.stemWord(word)
				if stemmedword.isdigit()==0 or (stemmedword.isdigit()==1 and len(stemmedword)<5):
					if not self.isword[stemmedword]:
						self.isword[stemmedword] = 1
						self.networds.append(stemmedword)
					self.dictIndex[stemmedword][str(self.DocumentCount)]["B"] +=1

		elif(tag == "page"):
			XMLWikiHandler.CurrentlyProcessing = 0
		elif (tag == "mediawiki" and documentsProcessed >9829050):
			self.writeFile(tempIndexFile)
			self.dictIndex.clear()
			self.isword.clear()
			self.titles.clear()
			self.networds.clear()
			tempIndexFile += 1

		self.CurrentData = ""

	def characters(self,content):
		if(self.CurrentData == "id" and XMLWikiHandler.CurrentlyProcessing == 1 and self.isIdDone == 1):
			self.ID += content
		elif(self.CurrentData == "title"):
			self.Title += content
		elif(self.CurrentData == "text"):
			self.Text += content


	def enterToDict(self,content,tag,ID):
		global dumpTokensCount
		if content:
			for data in content:
				dataTokens = tokiz(str(data))
				#print(dataTokens)
				dumpTokensCount += len(dataTokens)
				for word in dataTokens:
					word = str(word).lower()
					if(stopwords[word]):
						continue
					stemmedword = stemmer.stemWord(word)
					if stemmedword.isdigit()==0 or (stemmedword.isdigit()==1 and len(stemmedword)<5):
						if not self.isword[stemmedword]:
							self.isword[stemmedword] = 1
							self.networds.append(stemmedword)
						self.dictIndex[stemmedword][str(ID)][tag] +=1


	def writeFile(self,indexFileNumber):
		indexFile = "./index/"+str(indexFileNumber)+".txt"
		print ("Write index into ",indexFile)
		f = open(indexFile,"w")
		f.write("")
		f.close()
		self.networds.sort()
		f = open(indexFile,"a")
		for word in self.networds:
			if word == "" or word == " ":
				continue
			f.write(word)
			f.write("|")
			r = self.dictIndex[word]
			for key_id,val in r.items():
				f.write(key_id)
				f.write(":")
				for field,v in val.items():
					f.write(field)
					f.write(str(v))
					f.write(",")
				f.write("+")
			f.write("\n")
		f.close()
		titleFile = "./title/"+str(indexFileNumber)+".txt"
		print ("Write title into ",titleFile)
		f = open(titleFile,"w")
		f.write("")
		f.close()
		f = open(titleFile,"a")
		for title in self.titles:
			f.write(title)
			f.write(":")
			f.write(self.titles[title])
			f.write("\n")
		f.close()

def checkFile(number):
	path = "index/"+str(number)+".txt"
	if(os.path.exists(path)):
		return 1
	else:
		return 0

def deleteTempFile():
	try:
		os.remove("index/temp.txt")
	except:
		pass


def mergeFiles(numberOfFiles):
	while(checkFile(2)):
		iterate = 1
		newFileCount = 1
		while(iterate<numberOfFiles):
			if(checkFile(iterate) and checkFile(iterate+1)):
				#print(iterate,newFileCount)
				deleteTempFile()
				file = open("index/temp.txt","a")
				file1 = open("index/"+str(iterate)+".txt","r")
				file2 = open("index/"+str(iterate+1)+".txt","r")
				linesOf1 = file1.readline().strip("\n")
				linesOf2 = file2.readline().strip("\n")
				while (linesOf1 and linesOf2):
					if  linesOf1:
						wordDetail = linesOf1.split("|") 
						wordof1 = wordDetail[0]
						datailsOfWord1 = wordDetail[1]
					if  linesOf2:
						wordDetail = linesOf2.split("|") 
						wordof2 = wordDetail[0]
						datailsOfWord2 = wordDetail[1]
					if not linesOf1:
						file.write(linesOf2+"\n")
						linesOf2 = file2.readline().strip("\n")
					elif not linesOf2:
						file.write(linesOf1+"\n")
						linesOf1 = file1.readline().strip("\n")
					elif wordof2<wordof1:
						file.write(linesOf2+"\n")
						linesOf2 = file2.readline().strip("\n")
					elif wordof1<wordof2:
						file.write(linesOf1+"\n")
						linesOf1 = file1.readline().strip("\n")
					else:
						linesOf1 = linesOf1.rstrip('/')
						file.write(linesOf1)
						file.write(datailsOfWord2+"\n")
						linesOf1 = file1.readline().strip("\n")
						linesOf2 = file2.readline().strip("\n")
				file2.close()
				file1.close()
				file.close()
				os.remove("index/"+str(iterate)+".txt")
				os.remove("index/"+str(iterate+1)+".txt")
				copyfile("index/temp.txt","index/"+str(newFileCount)+".txt")
			else:
				#print(newFileCount)
				if(numberOfFiles!=1):
					copyfile("index/"+str(iterate)+".txt","index/"+str(newFileCount)+".txt")
					os.remove("index/"+str(iterate)+".txt")
			iterate +=2
			newFileCount +=1

		numberOfFiles = newFileCount
		#print("nc",newFileCount)
		deleteTempFile()

def divideFiles():
	chunks = documentLimit
	current = 2
	lineCount = 0
	file = open("index/1.txt")
	line = file.readline().strip("\n")
	# f = open(indexFile,"w")
	# f.write("")
	# f.close()
	writefile = open("index/"+str(current)+".txt",'a')
	while(line):
		if(lineCount%chunks==0):
			writefile.close()
			current+=1
			writefile = open("index/"+str(current)+".txt",'a')
		writefile.write(line)
		lineCount+=1
		line = file.readline()
	writefile.close()
	file.close()
	try:
		os.remove("index/1.txt")
	except:
		pass


if(__name__ == "__main__"):

	start = time.time()
	stopwordDictForm()
	f = []
	directoryPath = "PATH-TO-Corpus"
	for (dirpath, dirnames, filenames) in walk(directoryPath):
		f.extend(filenames)
	filePath = []
	for filenames in f:
		filePath.append(directoryPath+filenames)

	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces,0)
	Handler = XMLWikiHandler()
	parser.setContentHandler(Handler)
	for i in range(0,len(filePath)):
		print(filePath[i])
		parser.parse(filePath[i])
	mergeFiles(tempIndexFile)
	divideFiles()

	stop = time.time()
	print ("Time(sec): ", stop - start)
	print("DocumentsProcessed ", documentsProcessed-1)
	
