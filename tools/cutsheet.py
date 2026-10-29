"""Cut a Gemini sprite sheet (figures on a flat green background, side by side) into game frames.

python tools/cutsheet.py <sheet image> <output prefix> [height]
  -> <prefix>-0.png, <prefix>-1.png, ...: green keyed out, each frame cropped to the same canvas,
     feet on the bottom edge and centred on the feet, so the frames don't jump around when swapped.
"""
import sys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
H = int(sys.argv[3]) if len(sys.argv) > 3 else 384
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
# how green a pixel is: 0 on the character, 1 on the background, soft in between (JPEG edges)
k = np.clip(((g - np.maximum(r, b)) - 40) / 50, 0, 1)
alpha = 1 - k
# despill: pull green fringes back to the other channels
a[..., 1] = np.where(k > 0, np.minimum(g, np.maximum(r, b) + 10), g)
solid = alpha > 0.5

# figures are runs of columns with enough solid pixels; small gaps inside a figure are bridged
col = solid.sum(0) > 6
runs, x = [], 0
while x < len(col):
    if col[x]:
        s = x
        while x < len(col) and (col[x] or col[x:x + 2].any()):
            x += 1
        if x - s > 40:
            runs.append((s, x))
    x += 1

frames = []
for s, e in runs:
    m = solid[:, s:e]
    rows = np.where(m.any(1))[0]
    y0, y1 = rows[0], rows[-1] + 1
    foot = m[y1 - max(4, (y1 - y0) // 12):y1]  # the feet: anchor point for alignment
    fx = s + np.where(foot.any(0))[0].mean()
    frames.append((s, e, y0, y1, fx))

half = int(max(max(fx - s, e - fx) for s, e, _, _, fx in frames)) + 4
W, Hs = 2 * half, max(y1 - y0 for _, _, y0, y1, _ in frames) + 4
for i, (s, e, y0, y1, fx) in enumerate(frames):
    img = np.zeros((Hs, W, 4), np.uint8)
    x0, ys = int(round(fx)) - half, max(0, y1 - Hs)
    for dx in range(W):
        sx = x0 + dx
        if s <= sx < e:
            img[Hs - (y1 - ys):, dx, :3] = a[ys:y1, sx]
            img[Hs - (y1 - ys):, dx, 3] = alpha[ys:y1, sx] * 255
    im = Image.fromarray(img, 'RGBA')
    im = im.resize((round(W * H / Hs), H), Image.LANCZOS)
    im.save(f'{out}-{i}.png', optimize=True)
    print(f'{out}-{i}.png', im.size)
