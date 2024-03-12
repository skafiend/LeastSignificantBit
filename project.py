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
EXTENSIONS = (".jpeg", ".jpg")


# generate constants for our program.
# it takes our mask_high_bits as the first parameter, since max value for a subpixel = 255
# our min value for mask_high_bits = 11111110 or 254
# returns number_of_colors_per_byte, number_of_bits_per_color, mask_low_bits
def generate_parameters(high_bits: str):
    inverse_dict = {"0": "1", "1": "0"}
    low_bits = ""

    # our mask_low_bits should be opposite to mask_high_bits
    # we replace 0 with 1 and vise versa
    for i in high_bits:
        low_bits += inverse_dict[i]

    n_bits_to_write = high_bits.count("0")

    # to calculate how many colors we need to encode one byte (8 bits)
    # we should divide number_of_bits_to_encode / bits_per_color and round up the result in case we get a float
    # 8 / 1 = 8 colors, 8 / 3 = 3 colors and so on and so forth
    # floor division // returns the largest integer <= the result. therefore, we use the trick with negative numbers
    # since we don't want to import another math libraries
    # -8 / 3 = -2.66 or -8 // 3 = -3
    n_subpixels = -(-8 // n_bits_to_write)

    # int('string', 2) -> 2 is the base in other words 2 stands for binary system
    return (
        int(high_bits, 2),
        int(low_bits, 2),
        n_bits_to_write,
        n_subpixels,
    )


(
    mask_high_bits,
    mask_low_bits,
    bits_per_color,
    colors_per_byte,
) = generate_parameters("11110000")


def file_extension(path: str, extensions):
    name = os.path.basename(path).rstrip("\"'")
    if name.endswith(extensions) and os.path.exists(path):
        return path
    else:
        sys.exit(
            f"Don't use single quotes for the {path}, Supported image types: {EXTENSIONS}."
        )


def convert_to_array(image: str) -> ndarray:
    # Open our image as array
    # [[['r','g','b'],['r','g','b']],[['r','g','b'],['r','g','b']]]
    # shape = (rows=2,columns=2,colors=3)
    try:
        # our program doesn't support alpha channel as the JPG
        # in case our user renames PNG to JPG we use convert('RGB') we delete that channel whatsoever
        image = Image.open(image).convert("RGB")
        arr_image = np.array(image)
        image.close()
        return arr_image

    except FileNotFoundError:
        sys.exit(f"Your file {image} doesn't exist")


def encode(image: ndarray, char: str, start: int, end: int) -> None:
    count = 0
    for index, color in enumerate(image[start:end], start=start):
        # clear our LSB bits using mask and bitwise AND
        image[index] &= mask_high_bits
        # extract our LSB bits from 'char' using mask_low_bits and bitwise AND
        # that means that we convert all our left bits to 0
        # we will shift our bits to the right every iteration to get a new portion
        bites_to_write = (ord(char) >> count * bits_per_color) & mask_low_bits
        image[index] |= bites_to_write
        count += 1


def add_to_array(image: ndarray, msg: str) -> ndarray:
    msg = f"{msg}{END_OF_MSG}"
    # save our original shape
    arr_shape = np.shape(image)

    if image.shape[0] * image.shape[1] // colors_per_byte < len(msg):
        sys.exit("You image isn't big enough to be a container, choose another image")

    # and convert multidimensional array to one-dimensional
    image = np.reshape(image, -1)

    for i, char in enumerate(msg):
        # slice our chunk from the image
        start = i * colors_per_byte
        end = colors_per_byte * (i + 1)
        encode(image, char, start, end)

    image = image.reshape(arr_shape)
    return image


def decode(chunk, start, end) -> str:
    symbol = ""
    # when we've written our values we did it in reversed order from right to left
    # to extract the correct symbol we have to read them in reversed order as well
    for color in reversed(chunk[start:end]):
        # add 0 * bits_per_color before binary value
        symbol += f"{color & mask_low_bits:0{bits_per_color}b}"
    return chr(int(f"{symbol}", 2))


def read_from_array(image: ndarray) -> str:
    image = np.reshape(image, -1)
    msg = ""
    for index in range(len(image)):
        start = index * colors_per_byte
        end = colors_per_byte * (index + 1)
        symbol = decode(image, start, end)
        # we're deliberately using an unprintable character at the end of the message
        if not symbol.isprintable():
            return msg
        else:
            msg = msg + symbol


def main():

    example_text = (
        'Usage:'
        '\n\t\ttest_image.(jpg|jpeg) --message="a message to encode"'
        "\n\t\ttest_ENCODED.png --extract\n"
        "\n"
        "============================== WARNING =================================:\n"
        "Please, refrain from renaming your PNG files with alpha channel into JPG,\n"
        "\t\t\t\t\tALPHA CHANNEL WILL BE DELETED\n"
        "========================================================================"

    )

    parser = argparse.ArgumentParser(
        prog="Least Significant Bit Image",
        description="The script encodes a message using a JPG file/decodes the message from a PNG file",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("image", type=str, help="path to an image")
    parser.add_argument("--message", "-m", type=str, help="a message to encode")
    parser.add_argument(
        "--extract", "-e", action="store_true", help="extract the message from the image"
    )

    args = parser.parse_args()
    image_path = args.image
    message = args.message
    if message is None:
        message = ""
    extract_true = args.extract

    if all((image_path, message.isprintable(), not extract_true)):
        file_extension(image_path, EXTENSIONS)
        arr_img = convert_to_array(image_path)
        image = Image.fromarray(add_to_array(image=arr_img, msg=message)).convert("RGB")
        name = os.path.splitext(image_path)
        new_name = name[0] + "_ENCODED" + EXPORT_EXT
        image.save(new_name)
        image.show(new_name)
        print(f"Your message was successfully put into {new_name}. Congratulations!!!")
    elif all((image_path, not message, extract_true)):
        image = convert_to_array(image_path)
        print("Your encoded message is: ", read_from_array(image))
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
