import torch.nn as nn
import torch.nn.functional as F
from pointnet2_utils import PointNetSetAbstraction


class get_model(nn.Module):
    def __init__(self,num_class,normal_channel=True):
        super(get_model, self).__init__()
        in_channel = 6 if normal_channel else 3
        self.normal_channel = normal_channel
        self.sa1 = PointNetSetAbstraction(npoint=512, radius=0.2, nsample=32, in_channel=in_channel, mlp=[64, 64, 128], group_all=False)
        self.sa2 = PointNetSetAbstraction(npoint=128, radius=0.4, nsample=64, in_channel=128 + 3, mlp=[128, 128, 256], group_all=False)
        self.sa3 = PointNetSetAbstraction(npoint=None, radius=None, nsample=None, in_channel=256 + 3, mlp=[256, 512, 1024], group_all=True)
        self.fc1 = nn.Linear(1024, 512)
        self.bn1 = nn.BatchNorm1d(512)
        self.drop1 = nn.Dropout(0.4)
        self.fc2 = nn.Linear(512, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.drop2 = nn.Dropout(0.4)
        self.fc3 = nn.Linear(256, num_class)

    def forward(self, xyz):
        B, _, _ = xyz.shape
        if self.normal_channel:
            norm = xyz[:, 3:, :] # [B, D=3, N]
            xyz = xyz[:, :3, :] # [B, C=3, N]
        else:
            norm = None
        l1_xyz, l1_points = self.sa1(xyz, norm) # l1_xyz: [B, C=3, N=512], l1_points: [B, D=128, N=512]
        l2_xyz, l2_points = self.sa2(l1_xyz, l1_points) # l2_xyz: [B, C=3, N=128], l2_points: [B, D=256, N=128]
        l3_xyz, l3_points = self.sa3(l2_xyz, l2_points) # l3_xyz: [B, C=3, N=1], l3_points: [B, D=1024, N=1]
        x = l3_points.view(B, 1024) # [B, D=1024]
        x = self.drop1(F.relu(self.bn1(self.fc1(x)))) # [B, D=512]
        x = self.drop2(F.relu(self.bn2(self.fc2(x)))) # [B, D=256]
        x = self.fc3(x) # [B, D=n_class]
        x = F.log_softmax(x, -1)


        return x, l3_points



class get_loss(nn.Module):
    def __init__(self):
        super(get_loss, self).__init__()

    def forward(self, pred, target, trans_feat):
        total_loss = F.nll_loss(pred, target)

        return total_loss
