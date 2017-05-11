import torch
import torch.nn as nn
from math import pi
from torch.autograd import Variable


def normalize_left(adj):
    """Stochastic normalization :
    input : matrix W of size (batch, n, n)
    output : D^{-1}.W where D is the degree matrix
    """
    rowweight = adj.sum(2).expand_as(adj)
    # normalize
    adj = adj / rowweight
    return adj


def symmetric(adj):
    """makes adjacency symmetric by applying the transformation :
        w_ij <- sqrt(w_ij * w_ji)
    """

    adj = torch.sqrt(adj)
    return adj * adj.transpose(1, 2).contiguous()


def normalize(adj, epsilon=None):
    """symmetric stochastic normalization :
    input : matrix W of size (batch, n, n)
    output : D^{-1/2}.W.D^{-1/2} where D is the degree matrix
    """
    # normalize
    adj = normalize_left(adj)
    # symmetric
    adj = symmetric(adj)
    return adj


class Distance(nn.Module):
    """class manipulating Pytorch Variables to calculate an adjacency matrix from
    vertices of energy bursts described with the pseudorapidity and the azimuth
    angle.
    Every adjacency computing class should inherit from this class and redefine the
    method 'forward' by calling the method 'distances'."""

    def __init__(self):
        super(Distance, self).__init__()
        self.perimeter = 2 * pi

    def forward(self, *argl, **argd):
        raise NotImplementedError

    def distances(self, phi, eta):
        """computes squared distances with 2*pi cyclicity on phi.
        inputs: - phi : Tensor with 2*pi periodicity. size (batch, n)
                - eta : Tensor. size batch, n
        output: - min_dist : point by point distance Tensor. size (batch, n, n)
        """
        p = torch.stack((eta, phi % self.perimeter), dim=2)
        dist1 = self._distances(p)

        p = torch.stack((eta, (phi + self.perimeter / 2) % self.perimeter), dim=2)
        dist2 = self._distances(p)

        # pointwise minimum between dist1 and dist2
        min_dist = (dist1 + dist2) / 2 - torch.abs(dist1 - dist2) / 2

        return min_dist

    def _distances(self, p):
        """squared euclidean distances"""
        sqnorm = (p * p).sum(2)
        dotprod = p.bmm(torch.transpose(p, 1, 2))
        sqnorm = sqnorm.expand_as(dotprod)

        return(sqnorm + torch.transpose(sqnorm, 1, 2) - 2 * dotprod)


class DistanceKNN(Distance):
    def __init__(self, k):
        super(DistanceKNN, self).__init__()
        self.k = k

    def knn(self, dist):
        """returns a sparse Tensor containing the k-nearest neighbors
        inputs: - dist : point by point distance Tensor. size (batch, n, n)
        output: - knn : distance Sparse Tensor with `k` nearest neighbors. size (batch, n, n)
        """

        value, neigh = dist.sort(2)
        value = value[:, :, -self.k:]
        neigh = neigh[:, :, -self.k:]

        index = torch.LongTensor(range(dist.size()[1]))
        index = index.unsqueeze(0).unsqueeze(2).expand_as(neigh)

        batch = torch.LongTensor(range(dist.size()[0]))
        batch = batch.unsqueeze(1).unsqueeze(2).expand_as(neigh)

        if isinstance(dist, Variable):
            index = Variable(index)
            batch = Variable(batch)

        if dist.is_cuda:
            index = index.cuda()
            batch = batch.cuda()

        batch = batch.contiguous().view(-1)
        index = index.contiguous().view(-1)
        neigh = neigh.contiguous().view(-1)
        index = torch.stack((batch, index, neigh), dim=0)

        value = value.contiguous().view(-1)

        return value, index


if __name__ == '__main__':
    phi = Variable(torch.rand(1, 200))
    eta = Variable(torch.rand(1, 200))
    adj = DistanceKNN(2)
    dist = adj.distances(phi, eta)
    knn = adj.knn(dist)