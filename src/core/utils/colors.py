import numba as nb
import numpy as np


@nb.jit(
    nb.uint32(nb.uint8, nb.uint8, nb.uint8),
    cache=True, nopython=True, nogil=True
)
def encode_rgb(r: np.uint8, g: np.uint8, b: np.uint8) -> np.uint32:
    """
    Encodes RGB values (0-255) into a single 32-bit unsigned integer.

    Memory layout (big-endian):
    0x00RRGGBB (alpha channel unused).

    Args:
        r (uint8): Red channel (0-255).
        g (uint8): Green channel (0-255).
        b (uint8): Blue channel (0-255).
        
    Returns:
        uint32: Packed color value.
    """

    return (r << 16) | (g << 8) | b


@nb.jit(
    nb.types.UniTuple(nb.uint8, 3)(nb.uint32),
    cache=True, nopython=True, nogil=True
)
def decode_rgb(color: np.uint32) -> tuple[np.uint8, np.uint8, np.uint8]:
    """
    Decodes a 32-bit unsigned integer into RGB values.

    Args:
        color (uint32): Packed color value.
 
    Returns:
        tuple: (R, G, B) components as uint8.
    """

    r = (color >> 16) & 0xFF
    g = (color >> 8)  & 0xFF
    b = color & 0xFF

    return (r, g, b)


@nb.guvectorize(
    ['void(uint32[:], uint8[:], uint8[:])'], '(m),(n)->(n)',
    nopython=True, cache=True
)
def decode_rgb_vectorized(
    colors: np.ndarray,
    _: np.ndarray,
    result: np.ndarray
) -> np.ndarray:
    """
    Decodes a packed 32-bit unsigned integer into RGB components.

    Args:
        color (uint32): Packed color value.

    Returns:
        uint8[3]: 1D array containing (R, G, B) components.
    """

    color = colors[0]
    result[0] = (color >> 16) & 0xFF
    result[1] = (color >> 8) & 0xFF
    result[2] = color & 0xFF