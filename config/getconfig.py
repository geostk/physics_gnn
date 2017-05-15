from os.path import join
import argparse
from config.hyperparameters import hyperparameters
from config.default import defaultconfig, read_local


def readargs(project_dir, description):
    """Reads from stdin and returns arguments in a dictionary container"""

    parser = argparse.ArgumentParser(description=description)
    add_arg = parser.add_argument

    # training or testing
    add_arg('--mode', dest='mode',
            help="'test', 'train', 'description', 'plot', prepare_data', 'weight_average'")
    add_arg('--datatype', dest='datatype',
            help="'train' or 'test': type of data observed")

    # paths and modelname
    add_arg('--model', dest='model',
            help='model name')
    add_arg('--datadir', dest='datadir', default=join(project_dir, 'data'),
            help='path to data')
    add_arg('--netdir', dest='netdir', default=join(project_dir, 'models'),
            help='path to models directory')
    add_arg('--stdout', dest='stdout',
            help='redirects stdout')

    # model initialization parameters
    add_arg('--modeltype', dest='modeltype',
            help='type of architecture')
    add_arg('--batchnorm', dest='batchnorm', action='store_true',
            help='use batch normalization in layers')
    add_arg('--normalize', dest='normalize', action='store_true',
            help='normalize adjacency to be stochastic, use normalization factors a input feature')

    add_arg('--knn', dest='knn', type=int,
            help='K-NN sparsification for adjacency')

    add_arg('--dim', dest='dim', type=int, nargs='+',
            help='list of dimensions for GNN layers')
    add_arg('--deg', dest='deg', type=int, nargs='+',
            help='list of degrees for GNN layers')
    add_arg('--modifdeg', dest='modifdeg', type=int, nargs='+',
            help='list of degrees for GNN final modification layers')

    add_arg('--nb_layer', dest='nb_layer', type=int,
            help='number of layers in GNN')
    add_arg('--deg_layer', dest='deg_layer', type=int,
            help='degree of each layers in GNN')
    add_arg('--feature_maps', dest='feature_maps', type=int,
            help='number of feature maps for each layer in GNN')
    add_arg('--nb_modiflayer', dest='nb_modiflayer', type=int,
            help='number of modification layers in GNN')
    add_arg('--deg_modiflayer', dest='deg_modiflayer', type=int,
            help='degree of each modification layers in GNN')

    add_arg('--lr', dest='lr', type=float,
            help='initial learning rate')
    add_arg('--logistic_bias', dest='logistic_bias', type=float, default=0,
            help='biais applied before logistic regression')

    # training parameters
    add_arg('--epoch', dest='epoch', type=int,
            help='number of epoch for training')
    add_arg('--nb_batch', dest='nb_batch', type=int, default=float('+inf'),
            help='number of batchs for training')
    add_arg('--lr_thr', dest='lr_thr', type=float,
            help='threshold to update learning rate')
    add_arg('--lr_update', dest='lr_update', type=float,
            help='multiplication factor to update learning rate')
    add_arg('--lr_nbbatch', dest='lr_nbbatch', type=int,
            help='time window (in number of batch) to update learning rate')
    add_arg('--weightfunc', dest='weightfunc',
            help='name of function that should be applied to use custom weights')
    add_arg('--nb_save', dest='nb_save', type=int,
            help='number of batchs after which the model is saved')

    add_arg('--optimizer', dest='optimizer',
            help='optimizer method')
    add_arg('--loss', dest='loss',
            help='criterion function')

    # statistics parameters
    add_arg('--nbdisplay', dest='nbdisplay', type=int,
            help='number of batchs to average statistics')
    add_arg('--nbstep', dest='nbstep', type=int,
            help='number of batchs in one step for statistics')

    # graphics parameters
    add_arg('--zoom', dest='zoom', type=float, nargs='+',
            help='list of False Positive rate for zooming on ROC curve')

    # cuda
    add_arg('--cuda', dest='cuda', action='store_true',
            help='run model on GPU')

    # verbosity
    add_arg('--quiet', dest='quiet', action='store_true',
            help='decrease verbosity')

    args = parser.parse_args()
    return(args.__dict__)


class Config:
    def __init__(self, project_dir, description='python script used for GNN training or testing'):
        self.update_default(defaultconfig)
        self.update_default(read_local())
        param = readargs(project_dir, description)
        self.update(param)
        self.update(hyperparameters())  # code related parameters

        # some paths that depend on input
        self.netdir = join(self.netdir, self.model)
        self.graphdir = join(self.netdir, 'graphic')
        self.statdir = join(self.netdir, 'stat')

        self.check_mode()
        if self.mode == 'test':
            self.epoch = 1
        elif self.mode == 'train':
            self.datatype = 'train'

        self.init_same_layers_parameters()

    # mode should be either 'test' or 'train'
    def check_mode(self):
        if self.mode not in self.possible_modes:
            raise Exception('Unknown mode : {}\n'.format(self.mode))

    def __getattr__(self, name):
        """Raises error for missing parameters"""
        raise AttributeError('Missing parameter : {}\n'.format(name))

    def init_same_layers_parameters(self):
        """simple parameters for network initialisation with same parameters for
        each layer"""
        if self.nb_layer is not None:
            self.dim = [self.feature_maps] * (self.nb_layer - 1)
        if self.deg_layer is not None:
            self.deg = [self.deg_layer] * self.nb_layer
        if self.deg_modiflayer is not None:
            self.modifdeg = [self.deg_modiflayer] * self.nb_modiflayer

    def update_default(self, dictionnary):
        """adds key -> value from dictionnary if value is not None"""
        for key in dictionnary.keys():
            if dictionnary[key] is not None:
                self.__dict__[key] = dictionnary[key]

    def update(self, dictionnary):
        """adds key -> value from dictionnary if value is not None
        or if key is not mapped yet"""
        for key in dictionnary.keys():
            if key not in self.__dict__ or dictionnary[key] is not None:
                self.__dict__[key] = dictionnary[key]