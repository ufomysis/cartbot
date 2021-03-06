#!/usr/bin/python2

import network

import sys
import json
import pickle
import Image
from evdev import ecodes
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

################################################################################
# Handle command line args
################################################################################

if len(sys.argv) < 4:
    print("Usage: hidden_nodes neural_net.pickle train_data.json[+]")
    exit(1)

neural_net_file = open(sys.argv[2], "w")
#data_file = open(sys.argv[2]+".data", "w")
hidden_nodes =  int(sys.argv[1])

################################################################################
# Main
################################################################################

net = buildNetwork(network.input_nodes, hidden_nodes, network.output_nodes)
data_set = SupervisedDataSet(network.input_nodes, network.output_nodes)

print("Creating data set...")

for train_file in sys.argv[3:]:
    train_file = open(train_file,'r')
    training_data = json.load(train_file)
    train_file.close()
    for time in training_data:
        image_file, keys = training_data[time]
        input_values = network.image_to_input(Image.open(image_file), None)
        output_values = network.keys_to_output(keys)
        importance = 1
        if output_values[network.key_mapping[ecodes.KEY_LEFT]] or output_values[network.key_mapping[ecodes.KEY_RIGHT]]: 
            importance = 4
        #data_set.addSample(input_values, output_values, importance)
        for i in xrange(importance):
            data_set.addSample(input_values, output_values)

print("Training the network...")

min_delta = .0001
last_error = None
trainer = BackpropTrainer(net, data_set)
#trainer.trainUntilConvergence() # We want it to be verbose
for i in xrange(50):
    error = trainer.train()
    print("\t" + str(error))
    if last_error and abs(last_error - error) <= min_delta:
        print("ABORT ABORT!")
        break
    last_error = error

print("Saving to disk...")

pickle.dump(net,neural_net_file)
#pickle.dump(data_set,data_file)

