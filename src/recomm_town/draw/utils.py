def to_color(x: str) -> tuple[int, int, int]:
    assert x[0] == "#"
    r = int(x[1:3], 16)
    g = int(x[3:5], 16)
    b = int(x[5:7], 16)
    return (r, g, b)


def c(x: str) -> tuple[int, int, int, int]:
    assert x[0] == "#"
    r = int(x[1:3], 16)
    g = int(x[3:5], 16)
    b = int(x[5:7], 16)
    a = int(x[7:9] or "FF", 16)
    return (r, g, b, a)


def n():
    return (0, 0, 0, 0)


def crop_label(label: str, size: int) -> str:
    if len(label) <= size:
        return label
    else:
        return label[: size - 1] + "…"