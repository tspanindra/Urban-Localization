import os
import sys
import time
import json
import httplib2

from flask import Flask, request
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

def httpRequest(url=None):
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    return content

@app.route("/getData",  methods=['POST'])
def tagDownload():
	tag = request.form['tag']
	fileName = tag + ".txt"
	
	if(os.path.isfile(fname)):
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

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/getData",  methods=['POST'])

def getData():
   tag = request.form['tag']
   return tag

if __name__ == "__main__":
    app.run()
