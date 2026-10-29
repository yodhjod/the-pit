"""Cut a Gemini sprite sheet (figures on a flat green background, side by side) into game frames.

python tools/cutsheet.py <sheet image> <output prefix> [height]
  -> <prefix>-0.png, <prefix>-1.png, ...: green keyed out, each frame cropped to the same canvas,
     feet on the bottom edge and centred on the feet, so the frames don't jump around when swapped.
python tools/cutsheet.py --one [--flip] <image> <output file> <scale>
  -> one frame (a pose with loose bits flying off, like a hit), cropped to everything that isn't green,
     resized by <scale> (use the idle sheet's scale so the character keeps the same size; it's printed).
     --flip mirrors it: a whacked critter flies to the right (away from the explorer), so it must fall that way.
     --parts (after --one/--flip) splits off the loose bits: <file> keeps only the body, each other blob is saved as
     <file minus .png>-p0.png, -p1.png..., and <file minus .png>.json lists them with their centres in the body's pixels.
"""
import sys
import numpy as np
from PIL import Image

one = sys.argv[1] == '--one'
if one:
    sys.argv.pop(1)
flip = sys.argv[1] == '--flip'
if flip:
    sys.argv.pop(1)
parts = sys.argv[1] == '--parts'
if parts:
    sys.argv.pop(1)


def blobs(m):
    """4-connected labels of a boolean mask (no scipy here): returns the label image (-1 = empty) and blob sizes"""
    lab = np.full(m.shape, -1, np.int32)
    sizes = []
    H, W = m.shape
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x] >= 0:
            continue
        i, st, n = len(sizes), [(y, x)], 0
        lab[y, x] = i
        while st:
            cy, cx = st.pop()
            n += 1
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and lab[ny, nx] < 0:
                    lab[ny, nx] = i
                    st.append((ny, nx))
        sizes.append(n)
    return lab, sizes
src, out = sys.argv[1], sys.argv[2]
H = int(sys.argv[3]) if len(sys.argv) > 3 and not one else 384
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
# how green a pixel is: 0 on the character, 1 on the background, soft in between (JPEG edges)
k = np.clip(((g - np.maximum(r, b)) - 40) / 50, 0, 1)
alpha = 1 - k
# despill: pull green fringes back to the other channels
a[..., 1] = np.where(k > 0, np.minimum(g, np.maximum(r, b) + 10), g)
solid = alpha > 0.5

if one:
    rows, cols = np.where(solid.sum(1) > 3)[0], np.where(solid.sum(0) > 3)[0]
    y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    img = np.dstack([a[y0:y1, x0:x1], alpha[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8)
    sc = float(sys.argv[3])
    if flip:
        img = img[:, ::-1]
    im = Image.fromarray(np.ascontiguousarray(img), 'RGBA').resize((round((x1 - x0) * sc), round((y1 - y0) * sc)), Image.LANCZOS)
    if not parts:
        im.save(out, optimize=True)
        print(out, im.size)
        sys.exit()
    # --parts: the biggest blob is the body; other blobs big enough to matter (a phone, a bottle, a cap) become
    # their own images, thrown by the game; specks (motion lines, splashes) are dropped
    px = np.array(im)
    lab, sizes = blobs(px[..., 3] > 100)
    body = int(np.argmax(sizes))
    keep = [i for i, n in enumerate(sizes) if i != body and n >= 200]
    near = np.zeros_like(lab) - 1  # grow labels a few pixels so soft edges go with their blob
    for i in [body] + keep:
        near[lab == i] = i
    for _ in range(3):
        g2 = near.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.full_like(near, -1)  # shifted copy, no wrap-around at the edges
            sh[max(dy, 0):near.shape[0] + min(dy, 0), max(dx, 0):near.shape[1] + min(dx, 0)] = near[max(-dy, 0):near.shape[0] + min(-dy, 0), max(-dx, 0):near.shape[1] + min(-dx, 0)]
            g2 = np.where((g2 < 0) & (sh >= 0), sh, g2)
        near = g2
    base = out[:-4]
    meta = {'w': im.width, 'h': im.height, 'parts': []}
    for j, i in enumerate(keep):
        ys, xs = np.where(near == i)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        part = px[y0:y1, x0:x1].copy()
        part[near[y0:y1, x0:x1] != i] = 0
        f = f'{base}-p{j}.png'
        Image.fromarray(part, 'RGBA').save(f, optimize=True)
        meta['parts'].append({'f': f.split('/')[-1], 'x': float((x0 + x1) / 2), 'y': float((y0 + y1) / 2), 'w': int(x1 - x0), 'h': int(y1 - y0)})
        print(f, part.shape[1], part.shape[0])
    px[near != body] = 0
    Image.fromarray(px, 'RGBA').save(out, optimize=True)
    import json
    open(base + '.json', 'w').write(json.dumps(meta))
    print(out, im.size, len(keep), 'parts')
    sys.exit()

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
