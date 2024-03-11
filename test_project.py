import os.path, wget, pytest
import numpy as np
from PIL import Image
from project import (
    convert_to_array,
    add_to_array,
    read_from_array,
    file_extension,
    decode,
    encode,

)

# before the test start, create two files test.png and test.jpg
cwd = os.getcwd()
wget.download('https://file-examples.com/storage/fe0275ec7165ef4cb9b4af6/2017/10/file_example_JPG_1MB.jpg',
              out=f'{cwd}\\test.jpg')
wget.download('https://file-examples.com/storage/fe0275ec7165ef4cb9b4af6/2017/10/file_example_PNG_1MB.png',
              out=f'{cwd}\\test.png')
PATH = f'{cwd}\\test'


# file doesn't exists
def test_file_doesnt_exist():
    with pytest.raises(SystemExit):
        convert_to_array("C:\\Windows\\random.file")


@pytest.fixture
def extensions():
    return ".png", ".jpeg", ".jpg"


@pytest.fixture
def jpg_image():
    return f'{PATH}' + '.jpg'


@pytest.fixture
def png_image():
    return f'{PATH}' + '.png'


@pytest.fixture
def enc_png_image():
    return f'{PATH}' + '_encoded' + '.png'


@pytest.fixture
def enc_jpg_image():
    return f'{PATH}' + '_encoded' + '.jpg'


@pytest.mark.parametrize("path", ["C:\\test.txt", "C:\\test", "C:\\"])
def test_file_extension(path, extensions):
    with pytest.raises(SystemExit):
        file_extension(path, extensions)


# encoded array == extracted array
# if we convert our image to png, the order of elements must be the same
@pytest.mark.parametrize(
    ("original_image", "encoded_image"),
    [
        (
                'jpg_image',
                'enc_png_image',
        )
    ],
)
def test_arrays_equal(original_image, encoded_image, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, "Test message")
    enc_image = Image.fromarray(arr_enc_image)
    enc_image.save(request.getfixturevalue(encoded_image))
    arr_ext_image = convert_to_array(request.getfixturevalue(encoded_image))
    # test if all values in numpy.array are True
    assert (arr_enc_image == arr_ext_image).all() == True


@pytest.mark.parametrize(
    ("original_image", "encoded_image"),
    [
        (
                'jpg_image',
                'enc_jpg_image',
        )
    ],
)
# if we convert our image to jpg, the order of elements will be changed and the data will be lost
def test_arrays_not_equal(original_image, encoded_image, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, "Test message")
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
        add_to_array(small_container, 'Very very very very long message')


# test if we can encode and extract our message
@pytest.mark.parametrize(
    ("original_image", "encoded_image", "message"),
    [
        (
                'jpg_image',
                'enc_png_image',
                'Test message'
        )
    ],
)
def test_message(original_image, encoded_image, message, request):
    arr_image = convert_to_array(request.getfixturevalue(original_image))
    arr_enc_image = add_to_array(arr_image, message)
    enc_image = Image.fromarray(arr_enc_image)
    enc_image.save(request.getfixturevalue(encoded_image))
    arr_ext_image = convert_to_array(request.getfixturevalue(encoded_image))
    assert read_from_array(arr_ext_image) == message


@pytest.mark.parametrize(
    "image",
    [
        'jpg_image',
        'png_image',
        'enc_png_image',
        'enc_jpg_image',
    ],
)
def test_cleanup(image, request):
    os.remove(request.getfixturevalue(image))
