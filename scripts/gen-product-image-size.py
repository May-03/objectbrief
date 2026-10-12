#!/usr/bin/env python3
"""重新生成 src/data/productImageSize.ts —— 商品图的真实像素尺寸。

为什么需要这个文件:
    卡片图片是 `w-full` + `height: auto`, 浏览器在图片加载前只能用
    <img width/height> 属性推算占位高度。如果属性写死成 440x330 (4:3),
    而文件其实是 700x700, 图片一加载盒子就会从 281px 撑到 375px ——
    每张卡把下方内容顶下去 94px。属性写真实尺寸就不会有这个位移。

只用标准库 (自己解析 JPEG 的 SOF 段), 不需要装 Pillow。

用法:
    python3 scripts/gen-product-image-size.py
"""
import glob
import os
import struct

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "public", "images", "products")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "src", "data", "productImageSize.ts")

SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def jpeg_size(path):
    """返回 (width, height)。只解析到第一个 SOF 段。"""
    with open(path, "rb") as fh:
        if fh.read(2) != b"\xff\xd8":
            raise ValueError(f"{path}: 不是 JPEG")
        while True:
            byte = fh.read(1)
            if not byte:
                raise ValueError(f"{path}: 找不到 SOF 段")
            if byte != b"\xff":
                continue
            marker = fh.read(1)
            while marker == b"\xff":          # 填充字节
                marker = fh.read(1)
            code = marker[0]
            if code in (0xD8, 0xD9) or 0xD0 <= code <= 0xD7:
                continue
            length = struct.unpack(">H", fh.read(2))[0]
            if code in SOF_MARKERS:
                fh.read(1)                     # 精度
                height, width = struct.unpack(">HH", fh.read(4))
                return width, height
            fh.seek(length - 2, os.SEEK_CUR)


HEADER = """// 自动生成 — 商品图的真实像素尺寸, 供 <img width/height> 使用。
// 为什么要写真实尺寸: 卡片图片是 width:100% + height:auto, 浏览器会用
// width/height 属性先占位。属性写死成 440x330 (4:3) 而文件其实是 700x700,
// 图片加载完就会把盒子从 281px 撑到 375px, 每张卡把下方内容顶下去 94px。
// 重新生成: python3 scripts/gen-product-image-size.py

export const PRODUCT_IMAGE_SIZE: Record<string, [number, number]> = {
"""


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.jpg")))
    if not files:
        raise SystemExit(f"没有找到图片: {ROOT}")
    lines = [HEADER]
    for path in files:
        w, h = jpeg_size(path)
        lines.append(f'  "/images/products/{os.path.basename(path)}": [{w}, {h}],\n')
    lines.append("};\n")
    with open(OUT, "w") as fh:
        fh.writelines(lines)
    print(f"写出 {OUT}: {len(files)} 条")


if __name__ == "__main__":
    main()
