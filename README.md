# LSB Steganography 
#### Video Demo:  <URL HERE>
#### Description:
&nbsp; &nbsp; &nbsp; &nbsp;  This simple python script encodes your data using provided JPG image and converts the latter into PNG file with the encoded information. Those files are indistinguishable for the naked eye, and that gives you an opportunity not only hide the information itself, but also hide the fact that the data was transferred

&nbsp; &nbsp; &nbsp; &nbsp;  However, I wouldn't recommend using the script to protect your highly sensitive information for two reasons. The first is the algorithm it susceptible to <a href="https://daniellerch.me/stego/aletheia/lsbr-attack-en/">attacks on LSB replacement.</a> And the second is all the data is stored in plain text, in other words, the script encodes your data into an image but doesn't encrypt it in any way.

#### How it works:
&nbsp; &nbsp; &nbsp; &nbsp;  The script uses <a href="https://en.wikipedia.org/wiki/Bit_numbering#:~:text=In%20computing%2C%20the%20least%20significant,place%20of%20the%20binary%20integer.">the Least Significant Bit (LSB) </a> method to hide the message into an image which means it goes though some pixels in the provided JPG file and changes the rightmost bits in every of them. Using JPG for the purpose is very convenient, since they don't have the alpha channel and use <a href="https://en.wikipedia.org/wiki/Endianness#:~:text=A%20big%2Dendian%20system%20stores,byte%20at%20the%20smallest%20address.">the big endian format</a> for encoding. 
 
##### Encoding data:
- We read the image  and transform it into <a href="https://www.mathworks.com/help/matlab/math/multidimensional-arrays.html">a multidimensional array:</a> 
	- Save the shape of the array
	- Transform the array into a one dimensional array
- Go though the message:
	- Clear all the LSB bits from the current subpixel using ***the mask_high_bits***  <a href="https://realpython.com/python-bitwise-operators/#bitwise-and">the bitwise AND operator</a>:
	  ```python
	  # mask_high_bits = 0b11111100, image[index] is our subpixel = 0b00110111
	  # the result is 0b00110100, and now we're free to use the last two bits
	  # and write whatever we want
	  image[index] &= mask_high_bits
	  
	  # image[index] = 0b00110111 & 0b11111100
	  # image[index] = 0b00110100
	  ````
	-  Extract ***the bits_per_color*** according to  ***the mask_low_bits*** using <a href="https://realpython.com/python-bitwise-operators/#bitwise-and">the bitwise AND operator</a>
	  ```python
	  # count = 1, our char to write is 0b01000001 = 'A', bits_per_color = 2 
	  # and mask_low_bits = 0b00000011
	  bits_to_write = (ord(char) >> count * bits_per_color) & mask_low_bits
	  
	  # bits_to_write = 0b01000001 >> 1 * 2 & 0b00000011
	  # I added meaningless bits to the left to keep things simple. 0b00010000 == 0b010000
	  # bits_to_write = 0b00010000 & 0b00000011
	  # bits_to_write = 0b00000000
	  ```
	- Put them in a place from right to left using <a href="https://realpython.com/python-bitwise-operators/#right-shift">the right shift</a> and <a href="https://realpython.com/python-bitwise-operators/#bitwise-or">the bitwise OR operator</a> accordingly
	  ```python
	  # image[index] = 0b00110100, bits_to_write = 0b00000000
	  image[index] |= bits_to_write
	  
	  # image[index] = 0b00110100 |  0b00000000
	  # image[index] = 0b00110100
	  ```
- Reshape the array to its original form
- Save PNG file

##### Extracting data:
- We read the image  
- Transform the image into a one dimensional array
- Go through the array
	- Read the chunks of data in the right-to-left order extracting one symbol per chunk.
	  ```python
	  symbol = ""
	  # Every iteration we get a portion of recorded bits
	  # Iterations will go on until we get all 8 bits = 1 byte = 1 char
	  # Our encoded character is 'A' => the first iteration yields 10 => the next 00 
	  # and so on and so forth
	  # It's important to point out that when we recorded 'A' we wrote its bits 
	  # from right to left,so now we're reading them in the reversed order
	  for subpixel in reversed(chunk[start:end]):
	    symbol += f"{subpixel & mask_low_bits:0{bits_per_color}b}"
	    return chr(int(f"{symbol}", 2))
	    ```
- The script works as long as it doesn't encounter an unprintable symbol
- Show the message

