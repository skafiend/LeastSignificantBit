import sys
import os

from PIL import Image
import numpy as np
from numpy import ndarray
import argparse

# DON'T CHANGE THESE LINES UNLESS YOU KNOW WHAT YOU'RE DOING!!!!!!!
# END_OF_MSG MUST BE UNPRINTABLE
END_OF_MSG = ""
# saving files in 'jpg.' causes trouble reading the encoded data
EXPORT_EXT = ".png"
# we use this mark to clear our LSB bits
MASK_HIGH_BITS = 0b11111100
# we use this mask to extract bits from our character in right to left order
MASK_LOW_BITS = 0b00000011
# to encode one character (8bits) we need this amount of colors:
COLORS_PER_BYTE = 4
# every color (r, g, b) contains this amount of data:
BITS_PER_COLOR = 2
EXTENSIONS = (".png", ".jpeg", ".jpg")


def file_extension(path: str, extensions):
    ext = os.path.splitext(path)
    if ext[1] in extensions:
        return path
    else:
        sys.exit(f"Unsupported format {path}. Supported file types: {EXTENSIONS}.")


def convert_to_array(image: str) -> ndarray:
    # Open our image as array
    # [[['r','g','b'],['r','g','b']],[['r','g','b'],['r','g','b']]]
    # shape = (rows=2,columns=2,colors=3)
    try:
        image = Image.open(image)
        arr_image = np.array(image)
        image.close()
        return arr_image

    except FileNotFoundError:
        sys.exit(f"You file {image} doesn't exist")


def encode(image: ndarray, char: str, start: int, end: int) -> None:
    count = 0
    for index, color in enumerate(image[start:end], start=start):
        # clear our LSB bits using mask and bitwise AND
        image[index] &= MASK_HIGH_BITS
        # extract our LSB bits from 'char' using MASK_LOW_BITS and bitwise AND
        # that means that we convert all our left bits to 0
        # we will shift our bits to the right every iteration to get a new portion
        bites_to_write = (ord(char) >> count * BITS_PER_COLOR) & MASK_LOW_BITS
        image[index] |= bites_to_write
        count += 1


def add_to_array(image: ndarray, msg: str) -> ndarray:
    msg = f"{msg}{END_OF_MSG}"
    # save our original shape
    arr_shape = np.shape(image)

    if image.shape[0] * image.shape[1] // COLORS_PER_BYTE < len(msg):
        sys.exit("You image isn't big enough to be a container, choose another image")

    # and convert multidimensional array to one-dimensional
    image = np.reshape(image, -1)

    for i, char in enumerate(msg):
        # slice our chunk from the image
        start = i * COLORS_PER_BYTE
        end = COLORS_PER_BYTE * (i + 1)
        encode(image, char, start, end)

    image = image.reshape(arr_shape)
    return image


def decode(chunk, start, end) -> str:
    symbol = ""
    # when we've written our values we did it in reversed order from right to left
    # to extract the correct symbol we have to read them in reversed order as well
    for color in reversed(chunk[start:end]):
        # add 0 * BITS_PER_COLOR before binary value
        symbol += f"{color & MASK_LOW_BITS:0{BITS_PER_COLOR}b}"
    return chr(int(f"{symbol}", 2))


def read_from_array(image: ndarray) -> str:
    image = np.reshape(image, -1)
    msg = ""
    for index in range(len(image)):
        start = index * COLORS_PER_BYTE
        end = COLORS_PER_BYTE * (index + 1)
        symbol = decode(image, start, end)
        # we're deliberately using an unprintable character at the end of the message
        if not symbol.isprintable():
            return msg
        else:
            msg = msg + symbol


def main():
    example_text = (
        'text into an image: test_image.ext --message="Test text"'
        "\ntext from an image: test_ENCODED.png --extract"
    )

    parser = argparse.ArgumentParser(
        prog="Least Significant Bit Image",
        description="The program encodes/decodes a message into/from an image",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("image", type=str, help="path to an image")
    parser.add_argument("--message", "-m", type=str, help="a message to encode")
    parser.add_argument(
        "--extract", "-e", action="store_true", help="extract a message from an image"
    )

    args = parser.parse_args()
    image_path = args.image
    file_extension(image_path, EXTENSIONS)
    message = args.message
    if message is None:
        message = ""
    extract_true = args.extract

    if all((image_path, message.isprintable(), not extract_true)):
        arr_img = convert_to_array(image_path)
        image = Image.fromarray(add_to_array(image=arr_img, msg=message))
        name = os.path.splitext(image_path)
        new_name = name[0] + "_ENCODED" + EXPORT_EXT
        image.save(new_name)
        print(f"Your message was successfully put into {new_name}. Congratulations!!!")
    elif all((image_path, not message, extract_true)):
        image = convert_to_array(image_path)
        print("Your encoded message is: ", read_from_array(image))
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
