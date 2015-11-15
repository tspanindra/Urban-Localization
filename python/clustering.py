import glob,time
import os,re,sys
import string
import ast,json
import datetime,time
import numpy as np
from geopy.distance import vincenty

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
				t=datetime.datetime.fromtimestamp(int(t)).strftime("%m-%d-%Y")
				if t in temporal_events:
					temporal_events[t].append(coords)
				else:
					temporal_events[t]=[(coords)]
	f.close()
	return temporal_events
	
def build_dist_matrix(coords):
	n=len(coords)
	M = np.zeros((n,n))
	for i in range(n):
		for j in range(i,n):
			if i==j:
				M[i,j]=0.0
			else:
				M[i,j] = vincenty(coords[i], coords[j]).miles
				M[j,i] = M[i,j]
	return M
	
def find_coord_center(bin):
	slng=0
	slat=0
	n=len(bin)
	for c in bin:
		slng+=c[0]
		slat+=c[1]
	return (slng/n,slat/n)


def build_bins(coords,dist_threshold):
	bins=[]
	M = len(coords)
	visited = np.zeros(M)
	for i in range(M):
		if visited[i]==0:
			if len(bins)==0:
				bins.append([i])
				visited[i]=1
			else:
				for bin in bins:
					#find the apt bin to insert the item
					coord_bin=[]
					for j in bin:
						coord_bin.append(coords[j])
					curr_coord = coords[i]
					if visited[i]==0:
						avg_coord = find_coord_center(coord_bin)
						if vincenty(avg_coord, curr_coord).miles<=dist_threshold:
							bin.append(i)
							visited[i]=1
							break
				if visited[i]==0:
					bins.append([i])
					visited[i]=1
	return bins
	
def find_avg_dist(val,bin,dist_matrix):
	avg=0
	n=len(bin)
	for j in bin:
		avg+=dist_matrix[val,j]
	if n>1:
		avg=avg/(n-1)
	return avg

def silhouette(bins,dist_matrix):
	a={}
	b={}
	cnt=0
	try:
		for bin in bins:
			cnt+=1
			idx = bins.index(bin)
			new_blist = bins[:idx]+bins[idx+1:]
			for val in bin:
				idx = bin.index(val)
				new_bin = bin[:idx]+bin[idx+1:]
				a[val] = find_avg_dist(val,new_bin,dist_matrix)
				b[val] = find_avg_dist(val,new_blist[0],dist_matrix)
				for outer_b in new_blist[1:]:
					t = find_avg_dist(val,outer_b,dist_matrix)
					if t<b[val]:
						b[val]=t
		n=len(a)
		for i in range(n):
			a[i] = (b[i]-a[i])/max(a[i],b[i])
	except IndexError:
		bin = bins[0]
		for val in bin:
			a[val]=1
	return a			

def bin_analysis(coord_bins):
	bin_centers=[]
	bin_rank = []
	bin_length = []
	for bin in coord_bins:
		bin_centers.append(find_coord_center(bin))
		bin_length.append(len(bin))
	com = find_coord_center(bin_centers)
	
	for c in bin_centers:
		idx=bin_centers.index(c)
		dist=vincenty(c, com).miles
		if dist>0:
			rank=bin_length[idx]/dist
		else:
			rank=1
		bin_rank.append(rank)
		
	idx = bin_rank.index(max(bin_rank))
	return idx
	
			

def find_events(filename):
	temporal_events = parse_input(filename)
	folder = filename[:-4]
	if os.path.exists(folder):
		pass
	else:
		os.mkdir(folder)
	
	final_events={}
	for t in temporal_events:
		final_events_list=[]
		print "Creating files for date ",t
		if os.path.exists(os.path.join(folder,t)):
			pass
		else:
			os.mkdir(os.path.join(folder,t))
		
		path = os.path.join(folder,t,'coords.txt')
		coords = temporal_events[t]
		if os.path.exists(path):
			pass
		else:
			f=open(path,'w')
			print >> f,str(coords)
			f.close()
		
		path = os.path.join(folder,t,'coords.matrix')
		if os.path.exists(path):
			dist_matrix=np.load(path)
		else:
			dist_matrix=build_dist_matrix(coords)
			outfile = open(path,'w')
			np.save(outfile,dist_matrix)
			outfile.close()
			print "Saved distance matrix"
		
		logfile = open(os.path.join(folder,t,'binstat.log'),'w')
		
		dist_threshold=1
		path = os.path.join(folder,t,str(dist_threshold)+'.bin')
		f=open(path,'w')
		bins=build_bins(coords,dist_threshold)
		print >> f,str(bins)
		f.close()
		avg=silhouette(bins,dist_matrix)
		A=0
		for i in range(len(avg)):
			A+=avg[i]
		A=A/len(avg)
		max_A=A
		print >> logfile, str(dist_threshold)+'\t'+str(max_A)
		
		inc_dist_threshold=5
		while True:
			path = os.path.join(folder,t,str(inc_dist_threshold)+'.bin')
			f=open(path,'w')
			bins=build_bins(coords,inc_dist_threshold)
			print >> f,str(bins)
			f.close()
			avg=silhouette(bins,dist_matrix)
			A=0
			for i in range(len(avg)):
				A+=avg[i]
			A=A/len(avg)
			print >> logfile, str(inc_dist_threshold)+'\t'+str(A)
			if A>max_A:
				max_A=A
				inc_dist_threshold+=5
			else:
				break
		
		if inc_dist_threshold==5:
			dec_dist_threshold=1
			while dec_dist_threshold>0.1:
				path = os.path.join(folder,t,str(dec_dist_threshold)+'.bin')
				f=open(path,'w')
				bins=build_bins(coords,dec_dist_threshold)
				print >> f,str(bins)
				f.close()
				avg=silhouette(bins,dist_matrix)
				A=0
				for i in range(len(avg)):
					A+=avg[i]
				A=A/len(avg)
				print >> logfile, str(dec_dist_threshold)+'\t'+str(A)
				if A>max_A:
					max_A=A
					dec_dist_threshold/=2
				else:
					break
			if dec_dist_threshold==1:
				sel_dist=1
			else:
				sel_dist=dec_dist_threshold*2
		else:
			sel_dist=inc_dist_threshold-5
		
		logfile.close()
		print "Selected distance threshold ",sel_dist
		sel_file = str(sel_dist)+'.bin'
		path = os.path.join(folder,t)
		for filename in os.listdir(path):
			if filename.endswith("bin"):
				if filename==sel_file:
					pass
				else:
					os.remove(os.path.join(path,filename))
		
		f = open(os.path.join(folder,t,sel_file),'r')
		lines = [line.strip() for line in f.readlines()]
		bins = ast.literal_eval(lines[0])
		
		coord_bins = []
		for bin in bins:
			blist=[]
			for c in bin:
				blist.append(coords[c])
			coord_bins.append(blist)
		idx=bin_analysis(coord_bins)
		
		for idx_2 in bins[idx]:
			printer={}
			printer["lng"] = coords[idx_2][0]
			printer["lat"] = coords[idx_2][1] 
			final_events_list.append(printer)
		f.close()
		final_events[t] = final_events_list
	printer = {}
	printer["data"] = final_events
	return json.dumps(printer)

if __name__ == "__main__":
	filename=sys.argv[1]
	d=find_events(filename)
	outfile = open(filename[:-4]+'_localized.txt','w')
	print >> outfile, d
	outfile.close()
	print "Quitting program."
