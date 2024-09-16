'''
Example preprocssing script. Reads in SKRoot file for signal and WIT file for background.
Creates h5 file in WatChMaL format and npz file for train-val-test indices.
The SKRoot file must first be copied with the copy_branches program.
'''

import uproot3
import numpy as np
import h5py
print(h5py.__version__)

fsig = uproot3.open('/Users/Alejandro/Desktop/skdetsim.b8.detsim_rdir.r062361.r077336.prepreprocess.root')
fbg = uproot3.open('/Users/Alejandro/Documents/mcwit/data/redwit.074129.077889.lowfitwitE.root')
fout = h5py.File('SKROOT_B8_redwit_4MeV.h5','w')
findex = 'SKROOT_B8_redwit_4MeV_idxs.npz'

treesig=fsig['data']
#treebg=fbg['wit']
treebg=fbg['data']

nhitsig = treesig.array("nhits")
#nhitbg = treebg.array("nhit")
nhitbg = treebg.array("nhits")

nsig=len(nhitsig)
nbg=len(nhitbg)

nevsk_sig = np.arange(0,nsig,1)
nevsk_bg = np.arange(0,nbg,1)

hits_index_sig = np.append(0,np.cumsum(nhitsig)[:-1])
hits_index_bg = np.append(0,np.cumsum(nhitbg)[:-1])+hits_index_sig[-1]+nhitsig[-1]

fout.create_dataset("labels",data=np.append(np.ones(nsig,dtype="i4"),np.zeros(nbg,dtype="i4")))
fout.create_dataset("event_hits_index", data=np.append(hits_index_sig, hits_index_bg))
fout.create_dataset("nhit",data=np.append(nhitsig, nhitbg))
#fout.create_dataset("hit_pmt",data=np.append(np.bitwise_and(treesig.array("cables").flatten(),int(0xffff)),treebg.array("cable").flatten()),dtype='i4')
fout.create_dataset("hit_pmt",data=np.append(np.bitwise_and(treesig.array("cables").flatten(),int(0xffff)),np.bitwise_and(treebg.array("cables").flatten(),int(0xffff))))
#fout.create_dataset("hit_charge",data=np.append(treesig.array("Q").flatten(),treebg.array("q").flatten()))
fout.create_dataset("hit_charge",data=np.append(treesig.array("Q").flatten(),treebg.array("Q").flatten()))
# Calculate relative hit times below instead of the absolute times within the triggering window. 
#fout.create_dataset("hit_time",data=np.append(treesig.array("T").flatten(),treebg.array("t").flatten()))

fout.create_dataset("bsenergy",data=np.append(treesig.array("bsenergy").flatten(),treebg.array("bsenergy").flatten())) #koun
fout.create_dataset("nring",data=np.append(treesig.array("nring").flatten(),treebg.array("nring").flatten())) #koun
fout.create_dataset("angle",data=np.append(treesig.array("angle").flatten(),treebg.array("angle").flatten())) #koun
fout.create_dataset("evis",data=np.append(treesig.array("evis").flatten(),treebg.array("evis").flatten())) #koun
fout.create_dataset("ip",data=np.append(treesig.array("ip").flatten(),treebg.array("ip").flatten())) #koun
#fout.create_dataset("event_ids",data=np.append(treesig.array("nevsk").flatten(),treebg.array("nevsk").flatten())) #koun
fout.create_dataset("event_ids",data=np.append(nevsk_sig, nevsk_bg)) #koun
#fout.create_dataset("root_files",data=np.append(treesig.array("nrunsk").flatten(),treebg.array("nrunsk").flatten())) #koun


times_sig = treesig.array("T").tolist()
#times_bg = treebg.array("t").tolist()
times_bg = treebg.array("T").tolist()
for iEvt in range(nsig):
    if len(times_sig[iEvt])!=0:
#    print(iEvt, nsig)
     times_sig[iEvt] = np.array(times_sig[iEvt]) - (times_sig[iEvt][0] + times_sig[iEvt][-1])/2
for iEvt in range(nbg):  
    if len(times_bg[iEvt])!=0:
     times_bg[iEvt] = np.array(times_bg[iEvt]) - (times_bg[iEvt][0] + times_bg[iEvt][-1])/2

times_sig = np.array([t for evt in times_sig for t in evt])
times_bg = np.array([t for evt in times_bg for t in evt])
fout.create_dataset("hit_time",data=np.append(times_sig,times_bg),dtype='f4')

fout.close()

ntrain = int(0.8*(nsig+nbg))
nval = int(0.1*(nsig+nbg))

shuffle_idxs = np.arange(nsig+nbg)
np.random.shuffle(shuffle_idxs)

train_idxs = shuffle_idxs[:ntrain]
val_idxs = shuffle_idxs[ntrain:ntrain+nval]
test_idxs = shuffle_idxs[ntrain+nval:]

np.savez(findex, train_idxs=train_idxs, val_idxs=val_idxs, test_idxs=test_idxs)

# Use this line instead for a testing-only dataset.
#np.savez(findex, test_idxs = np.arange(nsig+nbg))


fsig.close()
fbg.close()
