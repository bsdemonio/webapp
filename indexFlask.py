#!/usr/bin/python
import glob;
#import pyPdf;
import subprocess;
import os;
import time;
from collections import Counter;
import re;
import MySQLdb;
import json;
import difflib
import random
from flask import Flask, request, redirect,render_template;
from flask import request, send_from_directory 
from flask.ext.script import Manager
from werkzeug import secure_filename
from flaskext.mysql import MySQL;
app = Flask(__name__);
mysql = MySQL();
app.config['MYSQL_DATABASE_USER'] = 'root';
app.config['MYSQL_DATABASE_PASSWORD'] = '';
app.config['MYSQL_DATABASE_DB'] = 'phd';
app.config['MYSQL_DATABASE_HOST'] = 'localhost';
mysql.init_app(app);


@app.route('/')
def index():
    return render_template('index.html');
def similar(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.5


def backSearch(search):
	onn = mysql.connect();
	cursor = mysql.connect().cursor();
	valuetoLocate = search['searchValue'];
	lettersAtTheBegining = valuetoLocate.split(' ');
	uniqueLettertoBuildQuery = [];
	for element in lettersAtTheBegining:
		if element[0] not in uniqueLettertoBuildQuery:
			uniqueLettertoBuildQuery.append(element[0]);
	query="";
	count = 0;
	for element in uniqueLettertoBuildQuery:
		query= query +"word like '"+element+"%'";
		count= count+1;
		if ( count < len(uniqueLettertoBuildQuery)):
			query= query +" OR ";
	#at this point we are going to need match query against	lettersAtTheBegining	
	cursor.execute("SELECT word,container from phdData where "+query);
	data = cursor.fetchall();
	#print(query);		
	#a = 'Hello, All you people'
	#b = 'hello, all You peopl'
	#print(similar(a, b))
	finalResult=[];
	indexPaper=[];
	cont = 0;
	for element in data:
		for element2 in lettersAtTheBegining:
			if(similar(element[0],element2)):
				if element2 not in indexPaper:
					indexPaper.append(element2);
					finalResult.append([element2,element[1]])
				else:
					for element6 in finalResult:
						if (element6[0] == element2):
							keyValue = finalResult.index(element6)
					searchPapersValues = finalResult[keyValue][1].split('|'); #we pull the existing papers before add or not add
					papersExisting = element[1].split('|');
					
					for element3 in papersExisting:
						if element3 not in searchPapersValues:
							searchPapersValues.append(element3);
					#at this point we are going to need the key to insert in our final results.
					
					#print(searchPapersValues)
					#print(finalResult.index([element2,element[1]]))
					newContainer = '|'.join(map(str, searchPapersValues));
					finalResult[keyValue][1]=newContainer;

	#at this point we have our list of words repeated related with papers, but we need to remove the repeated elements and
	#preserve their papers related before send them as json to angular			

	#print(finalResult)	
	for element in finalResult:
		keyValue = finalResult.index(element);
		finalResult[keyValue][1] = finalResult[keyValue][1].split('|');
	return json.dumps(finalResult);

@app.route('/search', methods=['POST'])
def search():
    return backSearch(json.loads(request.data.decode()));

def insertDBAuto(tabArray):
      db = MySQLdb.connect(host="localhost",user="root",passwd="",db="phd");
      cur = db.cursor();
      for element in tabArray:             
         sql=('select id from phdData where word like "'+element[0]+'"');
         cur.execute(sql);
         rows = cur.fetchall()
         existingID=0;
         if (len(rows) > 0):
            existingID= rows[0][0]; 
         if (existingID == 0):
            cur.execute('insert into phdData (word,container) values (%s,%s)',(element[0],element[1]));
         else:
            sql=('select container from phdData where word like "'+element[0]+'"');
            cur.execute(sql);
            rows = cur.fetchall()
            papersRelated = rows[0][0].split('|');
            if element[1] not in papersRelated:
               papersRelated.append(element[1])
            #print(papersRelated);
            #print("|".join(str(x) for x in papersRelated));
            newContainer = '|'.join(map(str, papersRelated))
            sql=('update phdData set container = "'+newContainer+'" where word like "'+element[0]+'"');
            cur.execute(sql);
            
      db.commit(); 
      print("success")
      #db.commit();
      #cur.execute("TRUNCATE TABLE "+tablename);
      #db.commit();

def readPDF(files):
      from StringIO import StringIO;
      for name in files:
         validateContent = "";
         route = '/Users/Alan/python/phd/webapp/static/pdfminer-20140328/tools/pdf2txt.py';
         #sp_args = ['python', route, '-p', '1', '-o', 'outtemp/'+name+'.out', self.directory + '/' + name];
         sp_args = ['python', route,  '-o', '/Users/Alan/python/phd/webapp/static/outtemp/'+name+'.out', '/Users/Alan/python/phd/webapp/static/pdf/' + name];
         sp = subprocess.Popen(sp_args);
         time.sleep(3);
         ins = open( '/Users/Alan/python/phd/webapp/static/outtemp/'+name+'.out', "r" );
         array = [];
         for line in ins:
             array.append( line );
         ins.close(); 
         cont =0;
         if (len(array) > 2):
            unique = [];
            fullPaper = [];
            for line in array:
               split = line.split( );
               for element in split:
                  stringWithNumbers = element;
                  stringWithoutNumbers=''.join(c if c not in map(str,range(0,10)) else "" for c in stringWithNumbers);
                  element = stringWithoutNumbers;
                  re.sub(r'[^\w]', ' ', element);
                  punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~''';
                  no_punct = "";
                  my_str = element;
                  for char in my_str:
                     if char not in punctuations:
                        no_punct = no_punct + char
                  element = no_punct.lower();
                  if len(element) > 3:
                     fullPaper.append(element);
                     if element in unique:
                        cont=cont +1;
                     else:
                        unique.append(element);
            #print len(fullPaper);
            #print len(unique);
            average = [];
            data = [];
            fullPaperwithcount = Counter(fullPaper);
            #print(fullPaperwithcount);
            mostbig = 0;
            for element in unique:
               avtemp = fullPaperwithcount[element];
               average.append([element,avtemp]);
               if avtemp in data:
                  mostbig=mostbig+1;
               else:
                  data.append(avtemp);
            #print(sorted(data));
            dOrder=sorted(data)

            n=len(dOrder)
            middle=n/2
            # codigo para calcular la media aritmetica
            #print 'Mediana Aritmetica: ', round(sum(data)*1.0/n,2)

            mediaAritmetica =  round(sum(data)*1.0/n,2);

            # codigo para calcular la mediana
            if n%2==0:
               mediana=(dOrder[middle+1] + dOrder[middle+2]) / 2
            else:
               mediana=dOrder[middle+1]*1

            #print ''
            #print 'Total datos', n
            #print 'Mediana: ', mediana
            #print len(average); 

            finalAverage = [];
            blacklist=['this','their','with','that','using','references','exercises','using','which','chapter','september'];
            for element in average:             
               if(element[1]/mediaAritmetica > .5 and element[0] not in blacklist): 
                  finalAverage.append([element[0],(element[1]/mediaAritmetica)]);
            
            processedInfo = [];
            for element in finalAverage:             
               processedInfo.append([element[0],name]);
            
            #self.insertDB(average,name); line to insert stuff in database not necessary now ... it would change
            #print(finalAverage);
            #print json.dumps(processedInfo);
            insertDBAuto(processedInfo)
            #print '---------------------------------';
         del array[:]
         del unique[:]
         #os.remove(path);
         #time.sleep(5)
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	f = request.files['file']
	f.save('/Users/Alan/python/phd/webapp/static/pdf/' + secure_filename(f.filename))
	files=[];
	files.append(f.filename)
	readPDF(files)
	return json.dumps('success');

if __name__ == '__main__':
    app.run(host='0.0.0.0');