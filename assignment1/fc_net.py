from layers import *
import numpy as np
from sklearn.metrics import accuracy_score


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
    for idx, dim in enumerate(layer_dims[1:]): # enumerate all hidden layers
        layer_num = str(idx+1)
        #params['W' + layer_num] = np.random.randn(layer_input_dim, dim)
        params['W' + layer_num] = np.random.randn(layer_input_dim, dim) * np.sqrt(2/layer_input_dim)
        params['b' + layer_num] = np.zeros(dim)
        layer_input_dim = dim

    # TODO: is below useless with softmax?
    # hidden_layer_last -> output
    num_layers = len(layer_dims)
    params['W' + str(num_layers)] = np.random.randn(layer_input_dim, num_classes)
    params['b' + str(num_layers)] = np.zeros(num_classes)

    return params


def L_model_forward(X, parameters, use_batchnorm, dropout):
    """
    forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SOFTMAX computation

    :param X: the data, numpy array of shape (input size, number of examples)
    :param parameters: the initialized W and b parameters of each layer
    :param use_batchnorm: a boolean flag used to determine whether to apply batchnorm after the activation
    :param dropout: Scalar between 0 and 1 giving dropout strength.
                    If dropout=1 then the network should not use dropout at all.
    :return: (the last post-activation value , a list of all the cache objects)
    """
    layer_input = X
    caches = []
    dropout_cache = {}  # cache for dropout layer
    num_layers = len([key for key in parameters.keys() if key.startswith('W')])
    use_dropout = dropout != 1

    for layer_idx in range(1, num_layers):
        W, b = parameters['W' + str(layer_idx)], parameters['b' + str(layer_idx)]
        layer_input, layer_cache = linear_activation_forward(layer_input, W, b, 'relu', use_batchnorm)
        caches.append(layer_cache)

        if use_dropout:
            layer_input, dropout_cache[layer_idx] = dropout_forward(layer_input, dropout)

    # last layer
    W, b = parameters['W' + str(num_layers)], parameters['b' + str(num_layers)]
    last_post_activation, layer_cache = linear_activation_forward(layer_input, W, b, 'softmax', use_batchnorm)
    caches.append(layer_cache)

    return last_post_activation, caches, dropout_cache


def compute_cost(AL, Y):
    """
    Implement the cost function defined by equation. The requested cost function is categorical cross-entropy loss.

    :param AL: – probability vector corresponding to your label predictions, shape (num_of_classes, number of examples)
    :param Y: the labels vector (i.e. the ground truth)
    :return: the cross-entropy cost
    """

    #TODO: check what happen when AL got invalid value for log
    return - np.sum((Y * np.log(AL))) / Y.shape[0]
    #return -np.sum((Y * np.log(AL)) + ((1-Y) * np.log(1-AL))) / Y.shape[0]


def L_model_backward(AL, Y, caches, dropout_cache):
    """
    Backward propagation process for the entire network.

    :param AL: the probabilities vector, the output of the forward propagation (L_model_forward)
    :param Y: the true labels vector (the "ground truth" - true classifications)
    :param caches: list of caches containing for each layer: a) the linear cache; b) the activation cache
    :return: a dictionary with the gradients
    """

    grads = {}
    num_layers = len(caches)
    use_dropout = len(dropout_cache) != 0

    # dL / dA = -(Y/A) + ((1-Y)/1-A)
    #TODO: fix parameters for softmax_backward (what should be dA)
    #last_layer_dA = -((Y / AL) - ((1-Y)/(1-AL)))

    last_layer_idx = num_layers
    dA, dW, db = linear_backward(AL - Y, caches[-1]['linear_cache'])
    grads['dA' + str(last_layer_idx)] = dA
    grads['dW' + str(last_layer_idx)] = dW
    grads['db' + str(last_layer_idx)] = db

    for layer_idx in reversed(range(1, num_layers)):
        if use_dropout:
            dA = dropout_backward(dA, dropout_cache[layer_idx])

        dA, dW, db = linear_activation_backward(dA , caches[layer_idx - 1], "relu")
        grads['dA' + str(layer_idx)] = dA
        grads['dW' + str(layer_idx)] = dW
        grads['db' + str(layer_idx)] = db

    return grads


def update_parameters(parameters, grads, learning_rate):
    """
    Updates parameters using gradient descent

    :param parameters: a python dictionary containing the DNN architecture’s parameters
    :param grads: a python dictionary containing the gradients (generated by L_model_backward)
    :param learning_rate: the learning rate used to update the parameters (the “alpha”)
    :return: – the updated values of the parameters object provided as input
    """

    num_layers = len([key for key in parameters.keys() if key.startswith('W')])

    for layer_idx in range(1, num_layers + 1):
        old_W, dW = parameters['W' + str(layer_idx)], grads['dW' + str(layer_idx)]
        old_b, db = parameters['b' + str(layer_idx)], grads['db' + str(layer_idx)]

        parameters['W' + str(layer_idx)] = old_W - learning_rate * dW
        parameters['b' + str(layer_idx)] = old_b - learning_rate * db

    return parameters


def L_layer_model(X, Y, x_val, y_val,
                  layers_dims,
                  learning_rate,
                  num_iterations,
                  batch_size,
                  use_batchnorm,
                  dropout=1):
    """
    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    :param X: the input data, a numpy array of shape (height*width , number_of_examples)
    :param Y: the “real” labels of the data, a vector of shape (num_of_classes, number of examples)
    :param x_val: same as X, for validation
    :param y_val: same as Y, for validation
    :param layers_dims: a list containing the dimensions of each layer, including the input
    :param learning_rate: the learning rate
    :param num_iterations: number of iterations
    :param batch_size: the number of examples in a single training batch.
    :param use_batchnorm: use batchnorm or not
    :param dropout: Scalar between 0 and 1 giving dropout strength.
                    If dropout=1 then the network should not use dropout at all.
    :return: (parameters, costs) - the parameters learnt by the system during the training (the same parameters
                                    that were updated in the update_parameters function) and the values of the cost
                                    function (calculated by the compute_cost function). One value is to be saved
                                    after each 100 training iterations (e.g. 3000 iterations -> 30 values)..
    """
    # initialization
    parameters = initialize_parameters([X.shape[1]] + layers_dims)
    costs = []
    accs = []

    count = 0
    for i in range(num_iterations):
        for X_batch, Y_batch in next_batch(X, Y, batch_size):

            # forward pass
            AL, caches, dropout_caches = L_model_forward(X_batch, parameters, use_batchnorm, dropout)

            # compute the cost and document it
            cost = compute_cost(AL, Y_batch)

            # backward pass
            grads = L_model_backward(AL, Y_batch, caches, dropout_caches)

            # update parameters
            parameters = update_parameters(parameters, grads, learning_rate)

            # TODO add stopping criterion.
            if count % 100 == 0:
                accs.append(predict(x_val, y_val, parameters))
                costs.append(cost)
            count += 1

    return parameters, costs, accs


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
    scores, _, _ = L_model_forward(X, parameters, use_batchnorm=False, dropout=1) # test time
    predictions = np.argmax(scores, axis=1)
    Y_flatten = np.argmax(Y, axis=1)
    # TODO: check if none of the classes is above 50%? 0.1 for all classes for example
    return accuracy_score(Y_flatten, predictions)


def next_batch(X, y, batchSize):
    # loop over our dataset X in mini-batches of size batchSize
    for i in np.arange(0, X.shape[0], batchSize):
        # yield a tuple of the current batched data and labels
        yield (X[i: i+batchSize, :], y[i: i+batchSize, :])

