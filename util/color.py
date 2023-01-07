def get_luminance(r8b: int, g8b: int, b8b: int) -> float:
    rs = r8b / 0xff
    gs = g8b / 0xff
    bs = b8b / 0xff

    r = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
    g = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
    b = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(luminance1: float, luminance2: float) -> float:
    if luminance1 < luminance2:
        return get_contrast_ratio(luminance2, luminance1)
    return (luminance1 + 0.05) / (luminance2 + 0.05)


if __name__ == '__main__':
    vanilla_luminance = get_luminance(0xfd, 0xde, 0x59)
    grey_luminance = get_luminance(0x2c, 0x2c, 0x2c)

    print(vanilla_luminance, grey_luminance)
    ratio = get_contrast_ratio(vanilla_luminance, grey_luminance)

    print(ratio)
