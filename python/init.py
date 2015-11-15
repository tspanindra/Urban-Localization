import os.path
import httplib2
import glob,time
import os,re,sys
import string
import ast,json
import datetime,time
import numpy as np
from math import radians, cos, sin, asin, sqrt
from sklearn.cluster import DBSCAN

from flask import Flask, request
from flask.ext.cors import CORS
from clustering import find_events

app = Flask(__name__)
CORS(app)

def httpRequest(url=None):
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    return content

@app.route("/getData",  methods=['POST'])
def getData():
	tag = request.form['tag']
	print tag
	fileName = tag + ".txt"
	if(os.path.isfile(fileName)):
		return "Success"

	data = []
	count = 0
	instagramJSON = ""
	unique_data = {}
	#nextUrl = "https://api.instagram.com/v1/tags/"+tag+"/media/recent?client_secret=f81d745a67c14f8da40da9017b98a7ca&client_id=bd5aa501f3a14929bf40a2730e272416
	nextUrl = "https://api.instagram.com/v1/tags/"+tag+"/media/recent?client_secret=deaceb7a1272478caf055dd87136c738&client_id=008d18f70616460789e708a19b1b4c21"
	count = 0
	try:
		while nextUrl:
			count = count +  1
			metadata = {}
			try:
				instagramJSON = httpRequest(nextUrl)
			except Exception, e:
				print count                 
				print e

			instagramDict = json.loads(instagramJSON)            
			nextUrl = instagramDict["pagination"]["next_url"]

			instagramData = instagramDict["data"]
            
			for picDict in instagramData:
				location = picDict["location"]               
				image_tags = picDict["tags"]
				image_tags_lower = []

				for downloaded_tag in image_tags :
					image_tags_lower.append(downloaded_tag.lower())
               
				if tag in image_tags_lower:
					if location != None:
						metadata["location"] = location
						metadata["tags"] = image_tags_lower
						metadata["created_time"] = picDict["created_time"]
						image = picDict["images"]["standard_resolution"]
						imageUrl = image["url"]

						if imageUrl not in unique_data.keys():
							unique_data[imageUrl] = 1
							print imageUrl
							metadata["imageUrls"] = imageUrl
							data.append(metadata)

							if(len(data) > 5):
								with open(fileName, 'w') as outfile:
									json.dump(data, outfile)								

								return "Success"
	except Exception, e:
		print e        

	with open(fileName, 'w') as outfile:
		json.dump(data, outfile)							

	return "Success"

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles/ 6371 for kms
    return c * r
    
def clustering_dbscan(pts):
	n = len(pts)
	X = np.zeros((n,n))
	for i in range(n):
		for j in range(n):
			X[i,j]=haversine(pts[i][1],pts[i][0],pts[j][1],pts[j][0])
	#dbsc = DBSCAN(eps=20, min_samples=30,metric='precomputed',algorithm='auto').fit(X) 
	dbsc = DBSCAN(eps=5,metric='precomputed',algorithm='auto').fit(X) 
	labels=dbsc.labels_	
	return labels

def parse_input(filename):
	temporal_events={}
	path = os.path.join(filename)
	f=open(path,'r')
	lines = [line.strip() for line in f.readlines()]
	for line in lines:
		data = ast.literal_eval(line)
		for d in data:
			if len(d['location'].keys())==4:
				coords=(d['location']['longitude'],d['location']['latitude'])
				t=d['created_time']
				t=datetime.datetime.fromtimestamp(int(t)).strftime("%m/%d/%Y")
				if t in temporal_events:
					temporal_events[t].append(coords)
				else:
					temporal_events[t]=[(coords)]
	f.close()
	return temporal_events



@app.route("/find_events_backend",  methods=['POST'])	
def find_events_backend():
	filename = request.form['filename']
	data = find_events(filename)
	return data
	'''
	fromdate = request.form['fromdate']
	todate = request.form['todate']

	temporal_events = parse_input(filename)
	current_date=datetime.datetime.strptime(fromdate,"%m/%d/%Y")
	end_date=datetime.datetime.strptime(todate,"%m/%d/%Y")
	slots=[]
	
	while current_date<=end_date:
		s = datetime.datetime.strftime(current_date,"%m/%d/%Y")
		slots.append(s)
		current_date += datetime.timedelta(1)
	
	candidates={}
	for k in slots:
		if k in temporal_events:
			pts = temporal_events[k]
			labels = clustering_dbscan(pts)
			u_labels = np.unique(labels)
			if len(u_labels)==1 and u_labels[0]==-1:
				candidates[k]=-1
			else:
				rt=np.where(u_labels!=-1)
				u_labels = u_labels[rt[0]]
				idx=np.where(labels==u_labels[0])[0]
				candidates[k]=[temporal_events[k][i] for i in idx]
				for l in u_labels:
					new_len = len(np.where(labels==l)[0])
					if len(candidates[k])<new_len:
						idx=np.where(labels==l)[0]
						candidates[k]=[temporal_events[k][i] for i in idx]
		else:
			candidates[k]=-1
	printer={}
	for k in candidates:
		if candidates[k]!=-1:
			if k in printer:
				coords=candidates[k]
				for c in coords:
					if c in printer[k]:
						printer[k][c]+=1
					else:
						printer[k][c]=1
			else:
				printer[k]={}
				coords=candidates[k]
				for c in coords:
					if c in printer[k]:
						printer[k][c]+=1
					else:
						printer[k][c]=1
		else:
			printer[k]=-1
	printer_new={}
	for k in printer:
		if printer[k]==-1:
			printer_new[k]=[]
		else:
			printer_new[k]=[]
			for c in printer[k]:
				d={}
				d["long"]=c[0]
				d["lat"]=c[1]
				d["count"]=printer[k][c]
				printer_new[k].append(d)
	output = {'data':printer_new}				
	return json.dumps(output)
	'''


def find_events1(filename, fromdate, todate):

	temporal_events = parse_input(filename)
	current_date=datetime.datetime.strptime(fromdate,"%m/%d/%Y")
	end_date=datetime.datetime.strptime(todate,"%m/%d/%Y")
	slots=[]
	
	while current_date<=end_date:
		s = datetime.datetime.strftime(current_date,"%m/%d/%Y")
		slots.append(s)
		current_date += datetime.timedelta(1)
	
	candidates={}
	for k in slots:
		if k in temporal_events:
			pts = temporal_events[k]
			labels = clustering_dbscan(pts)
			u_labels = np.unique(labels)
			if len(u_labels)==1 and u_labels[0]==-1:
				candidates[k]=-1
			else:
				rt=np.where(u_labels!=-1)
				u_labels = u_labels[rt[0]]
				idx=np.where(labels==u_labels[0])[0]
				candidates[k]=[temporal_events[k][i] for i in idx]
				for l in u_labels:
					new_len = len(np.where(labels==l)[0])
					if len(candidates[k])<new_len:
						idx=np.where(labels==l)[0]
						candidates[k]=[temporal_events[k][i] for i in idx]
		else:
			candidates[k]=-1
	printer={}
	for k in candidates:
		if candidates[k]!=-1:
			if k in printer:
				coords=candidates[k]
				for c in coords:
					if c in printer[k]:
						printer[k][c]+=1
					else:
						printer[k][c]=1
			else:
				printer[k]={}
				coords=candidates[k]
				for c in coords:
					if c in printer[k]:
						printer[k][c]+=1
					else:
						printer[k][c]=1
		else:
			printer[k]=-1
	printer_new={}
	for k in printer:
		if printer[k]==-1:
			printer_new[k]=[]
		else:
			printer_new[k]=[]
			for c in printer[k]:
				d={}
				d["long"]=c[0]
				d["lat"]=c[1]
				d["count"]=printer[k][c]
				printer_new[k].append(d)
	output = {'data':printer_new}				
	return json.dumps(output)
if __name__ == "__main__":
    #print find_events1("maroonvtour.txt","09/20/2015", "10/10/2015")
    app.run()
