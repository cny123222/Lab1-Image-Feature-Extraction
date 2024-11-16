import os
import sys
import glob
import argparse
from codes.hist import ColorHist, GrayHist, GradientHist

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

def parse_args(args):
    """
    读取命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--hist-type", choices=["color", "gray", "gradient", "all"], default="all", help="Options are ['color', 'gray', 'gradient']")
    parser.add_argument("--input-dir", type=str, default="images", help="path to folder of input images")
    parser.add_argument("--output-dir", type=str, default="hists", help="path to folder of output images")
    parser.add_argument("--output-type", type=str, default="png", help="layout of output images")

    args = parser.parse_args(args)
    return args


def get_image_paths(input_dir, extensions = ("jpg", "jpeg", "png", "bmp")):
    """
    从输入文件夹中找到所有图片文件
    """
    pattern = f"{input_dir}/**/*"
    img_paths = []

    for extension in extensions:
        img_paths.extend(glob.glob(f"{pattern}.{extension}", recursive=True))

    if not img_paths:
        raise FileNotFoundError(f"No images found in {input_dir}. Supported formats are: {', '.join(extensions)}")

    return img_paths


def create_hist(hist_type, img_paths, args):
    """
    创建直方图
    """

    hist_classes = {
        "color": ColorHist,
        "gray": GrayHist,
        "gradient": GradientHist
    }

    img_paths = tqdm(img_paths, desc=f"Processing {hist_type} histograms") if tqdm is not None else img_paths
    output_dir = os.path.join(args.output_dir, hist_type)

    for img_path in img_paths:
        original_filename = os.path.splitext(os.path.basename(img_path))[0]
        hist = hist_classes[hist_type](img_path)
        output_name = f"{original_filename}.{args.output_type}"
        hist.save_fig(output_dir, output_name)

    print(f"{len(img_paths)} figures successfully saved to {output_dir}")


def main(args):
    args = parse_args(args)

    img_paths = get_image_paths(args.input_dir)

    if args.hist_type == "all":
        for hist_type in ["color", "gray", "gradient"]:
            create_hist(hist_type, img_paths, args)
    
    else:
        create_hist(args.hist_type, img_paths, args)
        

if __name__ == "__main__":
    main(sys.argv[1:])