from layers import *
import numpy as np


class FullyConnectedNet:
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a sigmoid as last layer. This will also implement
    dropout and batch normalization as options.
    """
    
    def __init__(self, layer_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None):
        """
        Initialize a new FullyConnectedNet.
        
        Inputs:
        - layer_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then the network should not use dropout at all.
        - normalization: a boolean defines whether or not use batch norm
        """
        self.params = initialize_parameters([input_dim] + layer_dims + [num_classes])
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.num_layers = 1 + len(layer_dims)
        
        
def initialize_parameters(layer_dims):
    """
    input:
        an array of the dimensions of each layer in the network (layer 0 is the size of the flattened input, layer L is the output sigmoid)
    output:
        a dictionary containing the initialized W and b parameters of each layer (W1...WL, b1...bL).
    """
    params = {}
    layer_input_dim = layer_dims[0]
    num_classes = layer_dims[-1]

    # input-> hidden_layer_1 -> hidden_layer_2 -> ... -> hidden_layer_last
    for idx, dim in enumerate(layer_dims[1:-1]): # enumrate all hidden layers
        layer_num = str(idx+1)
        params['W' + layer_num] = np.random.randn(layer_input_dim, dim)
        params['b' + layer_num] = np.zeros(dim)
        layer_input_dim = dim

    # hidden_layer_last -> output
    num_layers = len(layer_dims) - 1
    params['W' + str(num_layers)] = np.random.randn(layer_input_dim, num_classes)
    params['b' + str(num_layers)] = np.zeros(num_classes)

    return params


def L_model_forward(X, parameters, use_batchnorm):
    """
    forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID computation

    :param X: the data, numpy array of shape (input size, number of examples)
    :param parameters: the initialized W and b parameters of each layer
    :param use_batchnorm: a boolean flag used to determine whether to apply batchnorm after the activation
    :return: (the last post-activation value , a list of all the cache objects)
    """

    # calculate the number of layers
    num_layers = len([key for key in d.keys() if key.startswith('W')])

    layer_input = X
    caches = {}
    for layer_idx in range(num_layers - 1):
        W ,b = parameters['W' + str(layer_idx)], parameters['b' + str(layer_idx)]
        layer_input, caches[layer_idx] = linear_activation_forward(layer_input, W, b, 'relu')
        if use_batchnorm:
            layer_input = apply_batchnorm(layer_input)

    # last layer
    W, b = parameters['W' + str(num_layers - 1)], parameters['b' + str(num_layers - 1)]
    last_post_activation, caches[num_layers - 1] = linear_activation_forward(layer_input, W, b, 'sigmoid')

    return last_post_activation, caches


def compute_cost(AL, Y):
    """
    Calculate the cost value by cross-entropy

    :param AL: probability vector corresponding to your label predictions, shape (1, number of examples)
    :param Y: the labels vector (i.e. the ground truth)
    :return: the cross-entropy cost
    """
    predictions_fixed = AL
    index_of_zeros = np.where(Y == 0)
    predictions_fixed[0][index_of_zeros] = 1 - predictions_fixed[0][index_of_zeros]

    return -np.sum(np.log(predictions_fixed)) / Y.shape[0]


def apply_batchnorm(activation):
    #TODO: calculate the batch normalization of the given activation
    return activation


def predict(X, Y, parameters):
    """
    Description:
        The function receives an input data and the true labels and calculates the accuracy of
        the trained neural network on the data.
    Input:
        X – the input data, a numpy array of shape (height*width, number_of_examples)
        Y – the “real” labels of the data, a vector of shape (num_of_classes, number of examples)
        parameters – a python dictionary containing the DNN architecture’s parameters
    Output:
        accuracy – the accuracy measure of the neural net on the provided data (i.e. the
        percentage of the samples for which the correct label receives over 50% of the
        confidence score). Use the softmax function to normalize the output values.
    """
    # scores: Array of shape (num_classes, number_of_examples) giving classification scores,
    # where scores[c, i] is the classification score for X[i] and class c.
    scores = L_model_forward(X, parameters, use_batchnorm=False) # TODO: ask Gilad where use_batchnorm should come from.
    probs = softmax(scores)
    labels_over_50 = np.where()

    # compare y and y_pred


def softmax(x):
    """
    Compute softmax values for each sets of scores in x
    """
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0) # sum row-wise

