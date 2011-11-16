from PIL import Image
from operator import itemgetter

def get_col(data, w, h, i):
    col = []
    for j in range(h):
        col.append(data[j*w + i])
    return col

def dist(a, b):
    # Borrowed from
    # http://chaoxuprime.com/2011/11/a-solution-to-Instagram-engineering-challenge-the-unshredder-in-haskell
    d = 0.
    for i, (x, y) in enumerate(zip(a, b)):
        d += (abs(x[0]-y[0]) + abs(x[1]-y[1]) + abs(x[2]-y[2]))**0.25
    return d

def unshred(im, ordering):
    unshredded = Image.new("RGBA", im.size)
    for i, si in enumerate(ordering):
        x1, y1 = 32*si, 0
        x2, y2 = x1 + 32, h
        slice_im = im.crop((x1, y1, x2, y2))
        unshredded.paste(slice_im, (i*32, 0))
    unshredded.show()

if __name__ == "__main__":
    im = Image.open("TokyoPanoramaShredded.png", "r")
    w, h = im.size
    data = im.getdata()
    slices= []

    # Extract the slice edges
    for i in range(w/32):
        left = get_col(data, w, h, i*32)
        right = get_col(data, w, h, (i+1)*32-1)
        slices.append((i, left, right))

    # Iteratively add slices to the output
    sl = slices.pop(0)
    ordering = [sl[0]]
    left_end = sl[1]
    right_end = sl[2]
    while len(slices) > 0:
        # left slices sorted by distance
        left_slices = sorted(
            [(sl, dist(sl[2], left_end)) for sl in slices],
            key=itemgetter(1))

        # right slices sorted by distance
        right_slices = sorted(
            [(sl, dist(right_end, sl[1])) for sl in slices],
            key=itemgetter(1))

        # Pick the best addition, left or right
        if left_slices[0][1] < right_slices[0][1]:
            left_slice = left_slices[0][0]
            ordering.insert(0, left_slice[0])
            left_end = left_slice[1]
            slices.remove(left_slice)
        else:
            right_slice = right_slices[0][0]
            ordering.append(right_slice[0])
            right_end = right_slice[2]
            slices.remove(right_slice)

    unshred(im, ordering)
