import keras
import os
import time
import math
import random
import glob
import numpy as np

import tensorflow as tf
import ROOT

from keras import backend as K
import rtf

from features import feature_dict

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
                max_threads = int(os.environ["OMP_NUM_THREADS"])
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
'''
inputLayers = keras.layers.Input(shape=(25,17))
conv = keras.layers.Conv1D(16)(inputLayers)
conv = keras.layers.Conv1D(16)(conv)
dense = keras.layers.Flatten()(conv)
dense = keras.layers.Dense(10)(dense)
classPrediction = keras.layers.Dense(5)(dense)

model = keras.models.Model(inputs=[inputLayers],outputs=[classPrediction])
model.summary()
'''
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
        if step==1:
            print train_batch_value
        if step%50==0:
            print "step",step
            for k in train_batch_value.keys():
                print " "*4,k,":",train_batch_value[k].shape
except tf.errors.OutOfRangeError:
    print 'Done reading files for %d steps.' % (step)
        