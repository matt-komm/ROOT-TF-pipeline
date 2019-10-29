'''===================================================================
Copyright 2019 Matthias Komm, Vilius Cepaitis, Robert Bainbridge, 
Alex Tapper, Oliver Buchmueller. All Rights Reserved. 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an "AS IS" 
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
or implied.See the License for the specific language governing 
permissions and limitations under the License.
==================================================================='''


import os
import glob
import numpy as np
import tensorflow as tf
from keras import backend as K
import rtf
import ROOT

from features import feature_dict
from plot import make_plot

def create_weight_histograms(input_file_list,features):
    hists_per_class = []
    chain = ROOT.TChain('jets','jets')
    for f in input_file_list:
        chain.AddFile(f)
        
    for variable in features['truth']['branches']:
        hist = ROOT.TH2F(
            variable,
            variable,
            10,1.3, 3.0, #log10(pt) binning
            3,-2.4,2.4 #eta binning
        )
        chain.Project(hist.GetName(),"global_eta:global_pt",variable)
        hist.SetDirectory(0)
        hists_per_class.append(hist)
        
    avg_events = np.mean(map(
        lambda h: h.Integral()/h.GetNbinsX()/h.GetNbinsY(),
        hists_per_class
    ))
    
    output_file = ROOT.TFile("weights.root","RECREATE")
    for hist in hists_per_class:
        for etabin in range(hist.GetNbinsY()):
            hist.SetBinContent(0,etabin+1,0)
            hist.SetBinContent(hist.GetNbinsX()+1,etabin+1,0)
            for ptbin in range(hist.GetNbinsX()):   
               
                xflavor = hist.GetBinContent(ptbin+1,etabin+1)
                if xflavor<4.:
                    hist.SetBinContent(ptbin+1,etabin+1,0.)
                else:
                    hist.SetBinContent(ptbin+1,etabin+1,avg_events/xflavor)
                
                hist.SetDirectory(output_file)
    output_file.Write()

def input_pipeline(
    input_file_list, 
    features, 
    batch_size, 
    repeat = 1, 
    max_threads = 6, 
    resample = False
):
    with tf.device('/cpu:0'):
        file_list_queue = tf.train.string_input_producer(
            input_file_list,
            num_epochs=repeat,
            shuffle=True
        )

        rootreaders = []
        resamplers = []
        
        if os.environ.has_key('OMP_NUM_THREADS'):
            try:
                max_threads = max(1,int(os.environ["OMP_NUM_THREADS"]))
            except Exception:
                pass
        
        for _ in range(min(len(input_file_list),max_threads)):
            reader_batch = max(10,int(batch_size/20.))
            reader = rtf.root_reader(file_list_queue, features, "jets", batch=reader_batch).batch()
            rootreaders.append(reader)
            if resample:
                weight = rtf.classification_weights(
                    reader["truth"],
                    reader["globalvars"],
                    "weights.root",
                    features['truth']['branches'],
                    [0, 1]
                )
                resampled = rtf.resampler(
                    weight,
                    reader
                ).resample()

                resamplers.append(resampled)
           
        batch = tf.train.shuffle_batch_join(
            resamplers if resample else rootreaders,
            batch_size=batch_size,
            capacity=5*batch_size,
            min_after_dequeue=2*batch_size,
            enqueue_many=True
        )
        is_signal = batch["truth"][:, 4] > 0.5
        batch["gen"] = rtf.fake_background(batch["gen"], is_signal, 0)

        return batch
        
create_weight_histograms(
    glob.glob('Samples/QCD_Pt-15to7000_unpacked_train1_[0-9]*.root'),
    feature_dict,
)

train_batch = input_pipeline(
    glob.glob('Samples/QCD_Pt-15to7000_unpacked_train1_[0-9]*.root'),
    feature_dict,
    batch_size=100,
    resample=True
)

init_op = tf.group(
    tf.global_variables_initializer(),
    tf.local_variables_initializer()
)

sess = K.get_session()
sess.run(init_op)

coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess, coord=coord)
 
pt_hists = []
ctau_hists = []

for variable in feature_dict['truth']['branches']:
    pt_hist = ROOT.TH1F(variable+"pt",variable,10,1.3,3.0)
    pt_hist.SetDirectory(0)
    pt_hists.append(pt_hist)
    
    ctau_hist = ROOT.TH1F(variable+"ctau",variable,10,-2.,5.)
    ctau_hist.SetDirectory(0)
    ctau_hists.append(ctau_hist)


step = 0    
try:
    while not coord.should_stop():
        step += 1
        train_batch_value = sess.run(train_batch)
        
        for i in range(train_batch_value['truth'].shape[0]):
            truth_index = np.argmax(train_batch_value['truth'][i])
            pt_value = train_batch_value['globalvars'][i,0]
            ctau_value = train_batch_value['gen'][i,0]
            pt_hists[truth_index].Fill(pt_value)
            ctau_hists[truth_index].Fill(ctau_value)
        
        if step%50==0:
            print "step",step
            for k in train_batch_value.keys():
                print " "*4,k,":",train_batch_value[k].shape
except tf.errors.OutOfRangeError:
    print 'Done reading files for %d steps.' % (step)
    
make_plot(pt_hists,ctau_hists)


        
