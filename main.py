from PIL import Image
from operator import itemgetter

def get_col(data, w, h, i):
    col = []
    for j in range(h):
        col.append(data[j*w + i])
    return col

def px_to_lum(r, g, b, _):
    return 0.2126*r + 0.7152*g + 0.0722*b

def dist(a, b):
    d = 0.
    for x, y in zip(a, b):
        d += (x-y)**2
    return d**0.5

if __name__ == "__main__":
    im = Image.open("TokyoPanoramaShredded.png", "r")
    im.show()
    print im.size
    w, h = im.size
    data = im.getdata()
    slices = []

    # Extract the slice edges
    for i in range(w/32):
        left = get_col(data, w, h, i*32)
        right = get_col(data, w, h, (i+1)*32-1)
        slices.append((left, right))

    # Calculate luminances
    slice_lums = []
    for left, right in slices:
        slice_lums.append((
            [px_to_lum(*px) for px in left],
            [px_to_lum(*px) for px in right]
        ))


    lefts = {}
    rights = {}
    for s in range(len(slice_lums)):
        this_slice = slice_lums[s]
        left_slices = sorted(
            [(i, dist(this_slice[0], slice_lums[i][1]))
                for i in range(len(slice_lums)) if i != s],
            key=itemgetter(1))
        right_slices = sorted(
            [(i, dist(this_slice[1], slice_lums[i][0]))
                for i in range(len(slice_lums)) if i != s],
            key=itemgetter(1))

        left = left_slices[0]
        right = right_slices[0]
        if left[0] == right[0]:
            if left[1] < right[1]:
                right = right_slices[1]
            else:
                left = left_slices[1]
        lefts[(right[0],s)] = (s, left[0])
        rights[(left[0],s)] = (s, right[0])

    for k, v in lefts.items():
        if v not in lefts:
            print k, v
            left_end = v[0]
            lefts.pop(k)
            break

    for k in rights.keys():
        if k[0] == left_end:
            left_start = k
            break

    ordering = [left_end]
    while True:
        ordering += [left_start[1]]
        if left_start not in rights:
            break
        else:
            left_start = rights[left_start]
    ordering.pop()

    unshredded = Image.new("RGBA", im.size)
    for i, slice in enumerate(ordering):
        x1, y1 = 32*slice, 0
        x2, y2 = x1 + 32, h
        slice_im = im.crop((x1, y1, x2, y2))
        unshredded.paste(slice_im, (i*32, 0))

    unshredded.show()
