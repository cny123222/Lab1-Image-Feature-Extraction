import os
import cv2
import warnings
import numpy as np
import matplotlib.pyplot as plt

hist_num = 0  # 直方图计数器, 便于显示绘图窗口

class Hist:
    """
    直方图父类
    """

    def __init__(self):

        global hist_num
        hist_num += 1

        # 初始化图像及序号
        self.fig = plt.figure(hist_num, figsize=(8, 6))
        self.index = hist_num

    def save_fig(
            self, 
            save_folder: str,
            save_name : str,
            dpi: int = 300
    ):
        """
        保存直方图

        参数:
        save_folder: 保存文件夹(允许不存在)
        save_name: 保存图像文件名称
        dpi: 图像分辨率, 默认值300

        返回值: None
        """
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        save_pth = os.path.join(save_folder, save_name)
        if os.path.exists(save_pth):
            warnings.warn(f"File '{save_name}' already exists in '{save_folder}'. Existing file will be overwritten.", UserWarning)
        self.fig.savefig(save_pth, dpi=dpi)

    def _set_hist_property(self):
        """
        设置直方图参数
        """
        # 设置轴标题及轴范围
        font_dict = {"family": 'serif', "weight": 'bold', "size": 15}
        if isinstance(self, ColorHist):
            plt.xlabel("Color Component", fontdict=font_dict)
            plt.ylabel("Proportion of Color Components", fontdict=font_dict)
            plt.ylim(0, max(self.proportions) * 1.2)
        elif isinstance(self, GrayHist):
            plt.xlabel("Grayscale Value", fontdict=font_dict)
            plt.ylabel("Proportion of Grayscale Values", fontdict=font_dict)
            plt.xlim(0, 255)
        elif isinstance(self, GradientHist):
            plt.xlabel("Gradient Intensity", fontdict=font_dict)
            plt.ylabel("Proportion of Gradient Intensities", fontdict=font_dict)
            plt.xlim(0, self._dynamic_xlim())

        # 设置轴刻度
        plt.xticks(fontproperties='serif', fontsize=15)
        plt.yticks(fontproperties='serif', fontsize=15)

        # 显示网格
        plt.grid(True, alpha=0.5, zorder=1)


class ColorHist(Hist):
    """
    颜色直方图
    """

    def __init__(
            self, 
            img_pth: str,
    ):
        """
        参数:
        img_pth: 图像路径
        """
        super().__init__()
        self.img = cv2.imread(img_pth, cv2.IMREAD_COLOR)  # 以彩色方式读入, 通道顺序为BGR
        self.channels = ["Blue", "Green", "Red"]
        self._create_hist()

    def _create_hist(self):
        """
        绘制颜色直方图
        """
        self.proportions = self._calc_RGB()  # 计算RGB分量

        plt.figure(self.index)
        bars = plt.bar(
            self.channels, 
            self.proportions, 
            color=["blue", "green", "red"], 
            width=0.9, 
            edgecolor="white", 
            linewidth=0.5,
            zorder=3
        )

        self._set_hist_property()

        # 显示柱高
        for bar, proportion in zip(bars, self.proportions):
            height = bar.get_height()
            plt.text(
                x=bar.get_x() + bar.get_width() / 2,
                y=height,                          
                s=f'{proportion:.3f}',                
                ha='center', 
                va='bottom',
                fontproperties='serif',
                fontsize=15                   
            )

        plt.close()

    def _calc_RGB(self):
        """
        计算三个颜色分量的相对比例
        """
        energy = self.img.sum(axis=(0, 1))  # 对三个通道分别求和
        return energy / energy.sum()  # 归一化


class GrayHist(Hist):
    """
    灰度直方图
    """

    def __init__(
            self, 
            img_pth: str,
    ):
        """
        参数:
        img_pth: 图像路径
        """
        super().__init__()
        self.img = cv2.imread(img_pth, cv2.IMREAD_GRAYSCALE)  # 以灰度方式读入
        self._create_hist()

    def _create_hist(self):
        """
        绘制灰度直方图
        """
        self.gray = self._calc_gray()

        plt.figure(self.index)
        bars = plt.bar(
            np.arange(256),
            self.gray, 
            width=1, 
            zorder=3
        )

        self._set_hist_property()

        plt.close()
        
    def _calc_gray(self):
        """
        计算各灰度值像素数目的比例
        """
        img_flat = self.img.flatten()
        gray_logit = np.bincount(img_flat, minlength=256)  # 计数
        return gray_logit / gray_logit.sum()  # 归一化


class GradientHist(Hist):
    """
    梯度直方图
    """

    def __init__(
            self, 
            img_pth: str,
    ):
        """
        参数:
        img_pth: 图像路径
        """
        super().__init__()
        self.img = cv2.imread(img_pth, cv2.IMREAD_GRAYSCALE)  # 以灰度方式读入
        self._create_hist()

    def _create_hist(self):
        """
        绘制梯度直方图
        """
        self.gradient, self.hist = self._calc_gradient()

        plt.figure(self.index)
        bars = plt.bar(
            np.arange(361),
            self.hist, 
            width=1, 
            zorder=3
        )

        self._set_hist_property()
        
        plt.close()

    def _calc_gradient(self):
        """
        计算梯度强度并划分区间
        """
        img_int = self.img.astype(np.int64) # Conversion from uint8 to int64 to avoid negative overflow
        grad_x = img_int[1:-1, 2:] - img_int[1:-1, :-2]
        grad_y = img_int[2:, 1:-1] - img_int[:-2, 1:-1]
        grad = np.sqrt(np.pow(grad_x, 2) + np.pow(grad_y, 2))
        hist, _ = np.histogram(grad, bins=np.arange(0, 362, 1))  # 划分区间并计数
        return grad, hist / hist.sum()
    
    def save_grad_img(self, save_folder, save_name):
        """
        绘制并保存边缘检测图像
        """
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        save_pth = os.path.join(save_folder, save_name)
        grad_img = self.gradient * (255 / self.gradient.max())  # 按比例提高亮度
        grad_img = 255 / (1 + np.exp(-(grad_img - 80) / 25))  # Sigmoid提高对比度, 参数可调
        cv2.imwrite(save_pth, grad_img)

    def _dynamic_xlim(self, epsilon=5e-4):
        """
        直方图x轴范围的动态调整
        """
        index = 360
        while index >= 0 and self.hist[index] <= epsilon:
            index -= 1
        return index if index > 200 else 200