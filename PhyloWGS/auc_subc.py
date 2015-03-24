# code to generate partial order plots

import cPickle

from numpy	  import *
from numpy.random import *
from tssb		import *
from util		import *
from util2 import *

#from ete2 import *

import sklearn.metrics as mt

#from sklearn.metrics import precision_recall_curve, roc_curve, auc

from clustering import *


import itertools

def compute_auc(fdir,dname):	
	ytrue = get_true()	
	m = 400 # number of genes / instances
	glist2 = loadtxt('./'+dname+'.ssm.txt',dtype='string')[1:,:]
	inds = [i for i,a in enumerate(glist2)]
	glist = [x[0] for x in glist2[inds]]
	glist = dict([(name,i) for i,name in enumerate(glist)])
	m = len(glist)
	S = zeros((m,m)) #similarity matrix (similar to pyclone)
	flist = os.listdir(fdir)
	ns = len(flist) #number of MCMC samples
	
	for idx,fname in enumerate(flist):
		if fname.find('Store')>-1: continue
		try:
			f=open('./'+fdir+'/'+str(fname))
			tssb = cPickle.load(f)
			wts, nodes = tssb.get_mixture()
					
			for node in nodes:
				data = node.get_data()
				
				pids = [glist[datum.name.lower()] for datum in data if datum.name.lower() in glist];npids=len(pids)
				pids=sort(pids)
				#ids=[(pids[i],pids[j]) for i in arange(npids) for j in arange(npids)]
				ids= itertools.combinations(pids, 2)			
				for id in ids: 
					S[id[0],id[1]]+=1 # same cluster
					#S[id[1],id[0]]+=1
		except EOFError:
			ns = ns -1
		finally:
			f.close()
			
	
	S[arange(m),arange(m)]=ns
	ypred = S*1./ns
	ids = triu_indices(m)
	
	ytrue=ytrue[ids]	
	ypred=ypred[ids]	
	
	precision, recall, thresholds = mt.precision_recall_curve(ytrue,ypred)
	aucpr = mt.auc(recall, precision)

	fpr, tpr, thresholds = mt.roc_curve(ytrue, ypred)
	aucroc = mt.auc(fpr, tpr)
	
	return aucpr,aucroc	

def get_true():
	clustering=[range(300),range(300,400)]
	return construct_matrix(clustering)

if __name__ == "__main__":
	dname = sys.argv[1]
	fdir = dname+'/best/'
	aucpr,aucroc=compute_auc(fdir,dname)
	print dname,round(aucpr,4),round(aucroc,4)
	f = open(dname+'.aupr.txt','w')
	f.write('%s %f %f' % (dname,round(aucpr,4),round(aucroc,4)))
	f.close()

