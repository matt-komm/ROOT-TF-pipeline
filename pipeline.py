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

def create_weight_histograms(input_file_list,features):
    hists_per_class = []
    for name in features['truth']

def input_pipeline(input_file_list, features, batch_size, repeat = 1, max_threads = 6):
    with tf.device('/cpu:0'):
        file_list_queue = tf.train.string_input_producer(
            input_file_list,
            num_epochs=repeat,
            shuffle=True
        )

        rootreader_op = []
        resamplers = []
        
        if os.environ.has_key('OMP_NUM_THREADS'):
            try:
                max_threads = max(1,int(os.environ["OMP_NUM_THREADS"]))
            except Exception:
                pass
        
        for _ in range(min(len(input_file_list),max_threads)):
            reader_batch = max(10,int(batch_size/20.))
            reader = rtf.root_reader(file_list_queue, features, "jets", batch=reader_batch).batch()
            rootreader_op.append(reader)
            '''
            if resample:
                weight = classification_weights(
                    reader["truth"],
                    reader["globalvars"],
                    os.path.join(outputFolder, "weights.root"),
                    branchNameList,
                    [0, 1]
                )
                resampled = resampler(
                    weight,
                    reader
                ).resample()

                resamplers.append(resampled)
           '''
        batch = tf.train.shuffle_batch_join(
            rootreader_op,
            batch_size=batch_size,
            capacity=5*batch_size,
            min_after_dequeue=2*batch_size,
            enqueue_many=True
        )
        is_signal = batch["truth"][:, 4] > 0.5
        batch["gen"] = rtf.fake_background(batch["gen"], is_signal, 0)

        return batch
        
train_batch = input_pipeline(
    glob.glob('Samples/QCD_Pt-15to7000_unpacked_train1_[0-9]*.root'),
    feature_dict,
    batch_size=100
)

test_batch = input_pipeline(
    glob.glob('Samples/QCD_Pt-15to7000_unpacked_test1_[0-9]*.root'),
    feature_dict,
    batch_size=100
)

init_op = tf.group(
    tf.global_variables_initializer(),
    tf.local_variables_initializer()
)

sess = K.get_session()
sess.run(init_op)

coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess, coord=coord)
 
step = 0    
try:
    while not coord.should_stop():
        step += 1
        train_batch_value = sess.run(train_batch)
        #if step==1:
        #    print train_batch_value
        if step%50==0:
            print "step",step
            for k in train_batch_value.keys():
                print " "*4,k,":",train_batch_value[k].shape
except tf.errors.OutOfRangeError:
    print 'Done reading files for %d steps.' % (step)
        
