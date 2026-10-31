"""Cut frames from a green-screen video clip (the character animating in place, locked camera) into game frames.

python tools/cutvideo.py <video> <output prefix> <scale> <frame> [<frame> ...]
  -> <prefix>-0.png, <prefix>-1.png, ...: the listed video frames (numbered from 1, as ffmpeg numbers them),
     green keyed out, only the largest blob kept (drops watermarks), all cropped to the same box (the union of the figure in every frame, so nothing jumps:
     the camera was locked), resized by <scale>.
  Paler green enclosed by the figure (seen through a clear plastic bag) is filled with pale grey plastic instead of being keyed out.
  Needs ffmpeg on the PATH.
"""
import os
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image

src, out, sc = sys.argv[1], sys.argv[2], float(sys.argv[3])
want = [int(x) for x in sys.argv[4:]]
tmp = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-v', 'error', '-i', src, os.path.join(tmp, 'f%04d.png')], check=True)


def key(a):
    """alpha 0-1 from how green each pixel is, scaled to the background's greenness (measured on the border)"""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gx = g - np.maximum(r, b)
    gb = np.median(np.concatenate([gx[0], gx[-1], gx[:, 0], gx[:, -1]]))
    lo, span = min(40, 0.45 * gb), min(50, 0.5 * gb)
    k = np.clip((gx - lo) / span, 0, 1)
    a[..., 1] = np.where(k > 0, np.minimum(g, np.maximum(r, b) + 10), g)  # despill
    return 1 - k, gx / max(gb, 1)


def outside(m):
    """True where a pixel is background connected to the image border (flood fill over not-m)"""
    H, W = m.shape
    seen = np.zeros_like(m)
    st = [(y, x) for y in (0, H - 1) for x in range(W)] + [(y, x) for x in (0, W - 1) for y in range(H)]
    while st:
        y, x = st.pop()
        if seen[y, x] or m[y, x]:
            continue
        seen[y, x] = True
        if y > 0: st.append((y - 1, x))
        if y < H - 1: st.append((y + 1, x))
        if x > 0: st.append((y, x - 1))
        if x < W - 1: st.append((y, x + 1))
    return seen


def main_blob(m):
    """the largest connected blob of m (drops watermarks and specks apart from the figure)"""
    H, W = m.shape
    lab = np.zeros(m.shape, np.int32)
    best, bn, n = 0, 0, 0
    for y0, x0 in zip(*np.nonzero(m[::4, ::4])):
        y0, x0 = y0 * 4, x0 * 4
        if lab[y0, x0]:
            continue
        n += 1
        st, cnt = [(y0, x0)], 0
        while st:
            y, x = st.pop()
            if y < 0 or x < 0 or y >= H or x >= W or lab[y, x] or not m[y, x]:
                continue
            lab[y, x] = n
            cnt += 1
            st += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
        if cnt > bn:
            best, bn = n, cnt
    return lab == best


frames = []
for f in want:
    a = np.asarray(Image.open(os.path.join(tmp, 'f%04d.png' % f)).convert('RGB')).astype(np.float32)
    al, gr = key(a)
    keep = main_blob(al > 0.1)
    al[~keep] = 0
    frames.append((a, al, gr))
# one crop for all: the union of the figure
U = np.any([al > 0.5 for _, al, _ in frames], axis=0)
ys, xs = np.nonzero(U)
y0, y1, x0, x1 = max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5
for i, (a, al, gr) in enumerate(frames):
    img = np.dstack([a[y0:y1, x0:x1], al[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(img, 'RGBA').resize((round((x1 - x0) * sc), round((y1 - y0) * sc)), Image.LANCZOS)
    px = np.array(im)
    grs = np.asarray(Image.fromarray((np.clip(gr[y0:y1, x0:x1], 0, 1) * 255).astype(np.uint8)).resize(im.size, Image.BILINEAR)) / 255
    # holes: background-coloured pixels the figure fully encloses (the bag) become pale plastic
    solid = px[..., 3] > 128
    # only paler green (seen through plastic): a gap between the bag and a leg is the full background green
    hole = ~solid & ~outside(solid) & (grs < 0.8)
    lum = px[..., :3].astype(np.float32).mean(2, keepdims=True)
    plastic = np.clip(170 + (lum - lum[hole].mean() if hole.any() else 0) * 0.5, 120, 235)
    px[hole, :3] = np.repeat(plastic, 3, 2)[hole].astype(np.uint8)
    px[hole, 3] = 235
    Image.fromarray(px, 'RGBA').save(f'{out}-{i}.png', optimize=True)
    print(f'{out}-{i}.png', im.size, int(hole.sum()), 'hole px')
