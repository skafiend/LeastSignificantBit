import os.path
import wget
import pytest
import numpy as np
from PIL import Image
from project import (
    convert_to_array,
    add_to_array,
    read_from_array,
    file_extension,
    decode,
    encode,
    generate_parameters,
)

pytestmark = pytest.mark.slow

cwd = os.getcwd()
PATH = f"{cwd}\\test"


@pytest.mark.slow
# before the test start, create test.jpg

def test_download_image():
    # even though the file is png in RGBA format, we'll delete the alpha channel
    wget.download(
        "https://cs50.harvard.edu/python/2022/psets/8/shirtificate/shirtificate.png",
        out=f"{cwd}\\test.jpg",
    )


# file doesn't exists
def test_file_doesnt_exist():
    with pytest.raises(SystemExit):
        convert_to_array("C:\\Windows\\random.file")


@pytest.fixture
def extensions():
    return ".jpeg", ".jpg"


@pytest.fixture
def jpg_image():
    return f"{PATH}" + ".jpg"


@pytest.fixture
def enc_png_image():
    return f"{PATH}" + "_encoded" + ".png"


@pytest.fixture
def enc_jpg_image():
    return f"{PATH}" + "_encoded" + ".jpg"


@pytest.mark.parametrize(
    "path",
    [
        "C:\\test.txt",
        "C:\\test",
        "C:\\",
        "C:\\Folder\\test.png",
        "'C:\\Folder\\test.png'",
    ],
)
def test_file_extension(path, extensions):
    with pytest.raises(SystemExit):
        file_extension(path, extensions)


# encoded array == extracted array
# if we convert our image to png, the order of elements must be the same
@pytest.mark.slow
@pytest.mark.parametrize(
    ("original_image", "encoded_image"),
    [
        (
            "jpg_image",
            "enc_png_image",
        )
    ],
)
# https://docs.pytest.org/en/7.1.x/reference/reference.html#request
def test_arrays_equal(original_image, encoded_image, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, "Test message")
    enc_image = Image.fromarray(arr_enc_image)
    enc_image.save(request.getfixturevalue(encoded_image))
    arr_ext_image = convert_to_array(request.getfixturevalue(encoded_image))
    # test if all values in numpy.array are True
    assert (arr_enc_image == arr_ext_image).all() == True


@pytest.mark.parametrize(
    "in_mask_high_bits, constants",
    [
        ("11111100", (252, 3, 2, 4)),
        ("11111110", (254, 1, 1, 8)),
        ("11111000", (248, 7, 3, 3)),
    ],
)
def test_parameters(in_mask_high_bits: str, constants: tuple):
    assert generate_parameters(in_mask_high_bits) == constants


@pytest.mark.slow
@pytest.mark.parametrize(
    ("original_image", "encoded_image"),
    [
        (
            "jpg_image",
            "enc_jpg_image",
        )
    ],
)
# if we convert our image to jpg, the order of elements will be changed and the data will be lost
# https://docs.pytest.org/en/7.1.x/reference/reference.html#request
def test_arrays_not_equal(original_image, encoded_image, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, "Test message")
    # we have to delete alpha channel, just in case
    enc_image = Image.fromarray(arr_enc_image)
    enc_image.save(request.getfixturevalue(encoded_image))
    arr_ext_image = convert_to_array(request.getfixturevalue(encoded_image))
    # test if all values in numpy.array are True
    assert (arr_enc_image == arr_ext_image).all() == False


@pytest.fixture
# create a small 4x4 pixels "image"
def small_container():
    return np.zeros((4, 4, 3))


# test a small container (image)
def test_small_container(small_container):
    with pytest.raises(SystemExit):
        add_to_array(small_container, "Very very very very long message")


# in the worst case we need 8 colors per byte to encode one char
# https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-parametrize
@pytest.fixture(
    params=[
        ([0, 0, 0, 0, 0, 0, 0, 0], "#"),
        ([255, 255, 255, 255, 255, 255, 255, 255], "V"),
        ([125, 125, 125, 125, 125, 125, 125, 125], " "),
    ]
)
def chunk(request):
    return request.param


# char == decode(encode(char))
# test how our encoding works on a one piece of data
def test_encode(chunk):
    encode(chunk[0], chunk[1], 0, 8)
    char = decode(chunk[0], 0, 8)
    assert char == chunk[1]


# test if we can encode and extract our message
@pytest.mark.slow
@pytest.mark.parametrize(
    ("original_image", "encoded_image", "message"),
    [
        (
            "jpg_image",
            "enc_png_image",
            "Strong people don't put others down. They lift them up. - Darth Vader",
        )
    ],
)
# https://docs.pytest.org/en/7.1.x/reference/reference.html#request
def test_message(original_image, encoded_image, message, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, message)
    enc_image = Image.fromarray(arr_enc_image)
    enc_image.save(request.getfixturevalue(encoded_image))
    arr_ext_image = convert_to_array(request.getfixturevalue(encoded_image))
    assert read_from_array(arr_ext_image) == message


@pytest.mark.slow
@pytest.mark.parametrize(
    "image",
    [
        "jpg_image",
        "enc_png_image",
        "enc_jpg_image",
    ],
)
def test_cleanup(image, request):
    os.remove(request.getfixturevalue(image))
