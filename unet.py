import torch
from torch import nn as nn


class UNet(nn.Module):

    def __init__(self, num_classes, start_filters, channels_in=1):
        # five sets of standard conv blocks
        super().__init__()
        self.conv1 = self.gen_conv_block(channels_in, start_filters, pooling=False)
        self.conv2 = self.gen_conv_block(start_filters, start_filters * 2)
        self.conv3 = self.gen_conv_block(start_filters * 2, start_filters * 4)
        self.conv4 = self.gen_conv_block(start_filters * 4, start_filters * 8)
        self.conv5 = self.gen_conv_block(start_filters * 8, start_filters * 16)

        # four sets of upsampling layers
        self.up6 = self.gen_upsampling_block(start_filters * 16, start_filters * 8)
        self.conv6 = self.gen_conv_block(start_filters * 16, start_filters * 8, pooling=False)

        self.up7 = self.gen_upsampling_block(start_filters * 8, start_filters * 4)
        self.conv7 = self.gen_conv_block(start_filters * 8, start_filters * 4, pooling=False)

        self.up8 = self.gen_upsampling_block(start_filters * 4, start_filters * 2)
        self.conv8 = self.gen_conv_block(start_filters * 4, start_filters * 2, pooling=False)

        self.up9 = self.gen_upsampling_block(start_filters * 2, start_filters)
        self.conv9 = self.gen_conv_block(start_filters * 2, start_filters, pooling=False)
        # 1x1xC conv with no upsampling
        self.conv10 = nn.Sequential(
            nn.Conv2d(start_filters, num_classes, kernel_size=1, stride=1),
            nn.Sigmoid()
        )

    @staticmethod
    def get_final_block(channels_in, num_classes):
        layers = [nn.Conv2d(channels_in, num_classes, kernel_size=1, stride=1)]
        if num_classes > 1:
            layers.append(nn.Softmax())
        else:
            layers.append(nn.Sigmoid())
        return nn.Sequential(*layers)

    @staticmethod
    def gen_upsampling_block(channels_in, channels_out):
        return nn.Sequential(
            nn.ConvTranspose2d(channels_in, channels_out,
                               kernel_size=2, stride=2),
            nn.ReLU()
        )

    @staticmethod
    def gen_conv_block(channels_in, channels_out, kernel_size=3,
                       pooling=True):
        if pooling:
            layers = [nn.MaxPool2d(kernel_size=2,stride=2)]
        else:
            layers = []
        layers += [
            nn.Conv2d(channels_in, channels_out, kernel_size, padding=[1, 1]),
            nn.ReLU(),
            nn.Conv2d(channels_out, channels_out, kernel_size, padding=[1, 1]),
            nn.ReLU()]
        return nn.Sequential(*layers)

    def forward(self, x):
        x1 = self.conv1(x)
        x2 = self.conv2(x1)
        x3 = self.conv3(x2)
        x4 = self.conv4(x3)
        x5 = self.conv5(x4)

        u6 = self.up6(x5)
        x6 = self.conv6(torch.cat([u6, x4], dim=1))

        u7 = self.up7(x6)
        x7 = self.conv7(torch.cat([u7, x3], dim=1))

        u8 = self.up8(x7)
        x8 = self.conv8(torch.cat([u8, x2], dim=1))

        u9 = self.up9(x8)
        x9 = self.conv9(torch.cat([u9, x1], dim=1))

        x10 = self.conv10(x9)
        return x10
