import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def run():
    body_data = pd.read_csv('../io/body_blueprints_file.dat',
                            names=['index', 'x', 'y', 'z', 'size'])
    joint_data = pd.read_csv('../io/joint_blueprints_file.dat',
                             names=['index', 'body1', 'body2',
                                    'x', 'y', 'z', 'ax', 'ay', 'az',
                                    'll', 'up', 'motor'])

    body_loc_data = body_data[['x', 'y', 'z']]
    joint_loc_data = joint_data[['x', 'y', 'z']]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(body_data['x'], body_data['y'], body_data['z'],
               marker='o')
    ax.scatter(joint_data['x'], joint_data['y'], joint_data['z'],
               marker='^')
    plt.show()


def check():
    body_data = pd.read_csv('../io/body_blueprints_file.dat',
                            names=['index', 'x', 'y', 'z', 'size'])
    joint_data = pd.read_csv('../io/joint_blueprints_file.dat',
                             names=['index', 'body1', 'body2',
                                    'x', 'y', 'z', 'ax', 'ay', 'az',
                                    'll', 'up', 'motor'])
    for j in joint_data:
        b1 = body_data.iloc[j['body1']]
        b2 = body_data.iloc[j['body2']]



body_data = pd.read_csv('../io/body_blueprints_file.dat', names=['index', 'x', 'y', 'z', 'size'])
joint_data = pd.read_csv('../io/joint_blueprints_file.dat', names=['index', 'body1', 'body2', 'x', 'y', 'z', 'ax', 'ay', 'az', 'll', 'up', 'motor'])
