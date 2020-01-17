
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import sys
from sklearn import preprocessing as pp


class LinearRegression:
    """
    http://openclassroom.stanford.edu/MainFolder/DocumentPage.php?course=MachineLearning&doc=exercises/ex2/ex2.html

    """

    def __init__(self, x, y, learning_rate=0.07, iterations=1600, normalize=True):
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
        if normalize:
            self.__x = self.normalize_features(x)
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

        # error = (((hyp - self.__y) ** 2).sum())[
        # hyp = self.__x.dot(self.__theta)
        cost = hyp - self.__y
        error = cost.transpose().dot(cost)
        return error.iloc[0, 0]/(2 * self.__samplesize)

    def update_para(self, hyp):
        '''
        :param theta: (self.__attributesnum +1 ) * 1
        :return:
        '''
        gd = self.compute_gradient_decent(hyp)
        self.__theta = self.__theta - gd

    def update_output(self, error):
        item = self.__theta.append(pd.DataFrame([error], index=['error']))
        item.index = self.__outputclms
        self.__output = self.__output.append(item.transpose())


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

    def predict(self, input_x):
        '''
        :param input_x: pd.Series, self.attributesize * 1
        :return: float
        '''
        assert isinstance(input_x, list)
        assert self.__attributesnum == len(input_x)
        for i in np.arange(self.__attributesnum):
            input_x[i] = (input_x[i] - self.__xstatics.iloc[i, 0])/self.__xstatics.iloc[i, 1]
        normalized = pd.DataFrame(([1]+input_x))
        pre = self.__theta.transpose().dot(normalized)
        return pre.loc[0, 0]

    def normalize_features(self, x):
        '''
        :param x: DataFrame m * attributes_size
        :return:
        '''
        # indexs = []
        # for i in np.arange(self.__attributesnum):
        #     indexs = indexs+['x'+str(i+1)]
        self.__xstatics = pd.DataFrame(columns=['mean', 'std'], index=np.arange(self.__attributesnum))
        for i in np.arange(self.__attributesnum):
            # scale attributes
            mean = x.loc[:, i].mean()
            std = x.loc[:, i].std()
            x.loc[:, i] = (x.loc[:, i] - mean) / std
            self.__xstatics.iloc[i, 0] = mean
            self.__xstatics.iloc[i, 1] = std
        return x


    def training(self):
        costs = pd.Series(0, index=np.arange(self.__iterations//50+1))
        for i in range(self.__iterations + 1):
            hyp = self.get_hypothesis()
            self.update_para(hyp)
            if i % 50 == 0:
                error = self.update_cost_function(hyp)
                self.update_output(error)
                try:
                    costs[i//50] = error
                    if i % 100 == 0:
                        print('iteration = ', str(i), "learning rate: ", str(self.__learning_rate))
                        for j in range(self.__attributesnum + 1):
                            print(self.__outputclms[j], '  =  ',  self.__theta.iloc[j, 0])
                        print('error = ', error, '\n')
                except OverflowError:
                    costs[i // 50] = sys.maxsize
                    costs[(i//50+1):] = np.nan
                    print("overshot caused by large learning rate ??? at iteration: ", str(i), " with learning rate: ",
                          str(self.__learning_rate))
                    return costs

                # self.plot_model(self.get_hypothesis())
        # try:
        #     self.plot_error((0xFF0000 + i * 20))
        # except AssertionError:
        #     print("\ncan only plot 2-D figures :) \n")
        return costs


# Single attribute regression
# x = pd.read_csv('ex2Data/ex2x.dat', header=None)
# y = pd.read_csv('ex2Data/ex2y.dat', header=None)
# lr = LinearRegression(x, y, normalize=False)

# Multivariate regression
x = pd.read_csv('ex3Data/ex3x.dat',sep='\s+',header=None,engine='python')
y = pd.read_csv('ex3Data/ex3y.dat', header=None)
# y = pd.DataFrame(pp.StandardScaler().fit_transform(y))


learning_rates = [0.01, 0.03, 0.1, 0.3, 1, 3]
analyze_cost = {}
for rate in learning_rates:
    lr = LinearRegression(x, y, learning_rate=rate, iterations=1000)
    costs = lr.training()
    analyze_cost.update({rate: costs})
out = pd.DataFrame(analyze_cost)
out.plot()
plt.show()
# predict = lr.predict([1650, 3])
# print('estimated value = ', predict)



