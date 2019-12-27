
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


class LinearRegression:
    """
    http://openclassroom.stanford.edu/MainFolder/DocumentPage.php?course=MachineLearning&doc=exercises/ex2/ex2.html

    """

    def __init__(self, x, y, learning_rate=0.07, iterations=1600):
        '''

        :param feed:
        :param instrument:
        :param x: DataFrame, attributes, variable
        :param y: DataFrame
        :param learning_rate:
        :param iterations:
        '''
        self.__learning_rate = learning_rate
        self.__iterations = iterations
        self.__samplesize = len(x)
        self.__attributesnum = x.columns.size
        assert (self.__samplesize == len(y))
        # m * (self.__attributesnum +1 )
        self.__x = pd.concat([pd.Series(1, index=np.arange(0, self.__samplesize)), x], axis=1)
        self.__x.columns = np.arange(0, self.__attributesnum + 1)
        # m * 1
        self.__y = y
        # (self.__attributesnum +1 ) * 1
        self.__theta = pd.DataFrame(pd.Series(0, self.__x.columns))
        self.init_output()

    def init_output(self):
        a = np.zeros(shape=(1, self.__attributesnum + 2))
        clms = []
        for i in range(self.__attributesnum + 1):
            clms.append('theta'+str(i))
        clms.append('error')
        self.__outputclms = clms
        self.__output = pd.DataFrame(a, columns=self.__outputclms)

    def get_hypothesis(self):
        '''
        :model:   h(x) = theta0 * x0 + theta1 * x1 + ...
                  x0 = [1, 1, ..., 1]
        :return: m * 1
        '''

        return self.__x.dot(self.__theta)

    def compute_gradient_decent(self, hyp):
        # gd =(((model-self.__y).transpose()).dot(self.__x)).transpose()
        xt = self.__x.transpose()
        gd = xt.dot(hyp - self.__y)
        return gd * self.__learning_rate/self.__samplesize

    def update_cost_function(self, hyp):
        '''
        J(theta) = (sum{hypothesis - y} ** 2)/ (2 * m)
        :return: float
        '''

        error = (((hyp - self.__y) ** 2).sum())[0]
        return error/(2 * self.__samplesize)

    def update_para(self, position):
        '''
        :param theta: (self.__attributesnum +1 ) * 1
        :return:
        '''
        hyp = self.get_hypothesis()
        gd = self.compute_gradient_decent(hyp)
        self.__theta = self.__theta - gd
        if position % 50 == 0:
            error = self.update_cost_function(hyp)
            item = self.__theta.append(pd.DataFrame([error], index=['error']))
            item.index = self.__outputclms
            self.__output = self.__output.append(item.transpose())
            return error
        return None

    def plot_model(self, hyp):
        plt.scatter(self.__x.iloc[:, 1], self.__y, c='g')
        plt.scatter(self.__x.iloc[:, 1], hyp, c='r')

    def understanding_error(self):
        error = np.zeros((100, 100))
        theta0 = np.linspace((-3, 3, 100))
        theta1 = np.linspace(-1, 1, 100)


    def plot_error(self, color):
        assert(self.__attributesnum == 1)

        theta0 = self.__output[self.__outputclms[0]]
        theta1 = self.__output[self.__outputclms[1]]
        errors = self.__output[self.__outputclms[2]]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # ax.scatter(theta0, theta1, errors, c='#FF00FF', marker='o')

        # ax = Axes3D(plt.figure())
        theta0, theta1 = np.meshgrid(theta0, theta1)
        surf = ax.plot_surface(theta0, theta1, errors, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
        # Add a color bar which maps values to colors.
        # fig.colorbar(surf, shrink=0.5, aspect=5)
        # ax.contour(theta0, theta1, errors, cmap=cm.coolwarm)
        ax.set_xlabel(self.__outputclms[0])
        ax.set_ylabel(self.__outputclms[1])
        ax.set_zlabel(self.__outputclms[2])
        plt.show()

    def run(self):
        for i in range(self.__iterations + 1):
            error = self.update_para(i)
            if i % 100 == 0:
                print(' iteration = {0} model parmaters:\n theta0 = {1}\n theta1 = {2}\n  error = {3}\n'.
                      format(i, self.__theta.iloc[0,0], self.__theta.iloc[1,0], error))
                # self.plot_model(self.get_hypothesis())
        self.plot_error((0xFF0000 + i * 20))


x = pd.read_csv('ex2Data/ex2x.dat', header=None)
y = pd.read_csv('ex2Data/ex2y.dat', header=None)
lr = LinearRegression(x, y)
lr.run()
