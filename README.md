# LSB Steganography 
#### Video Demo:  <URL HERE>
#### Description:
&nbsp; &nbsp; &nbsp; &nbsp;  This simple python script encodes your data using provided JPG image and converts the latter into PNG file with the encoded information. Those files are indistinguishable for the naked eye, and that gives you an opportunity not only hide the information itself, but also hide the fact that the data was transferred

&nbsp; &nbsp; &nbsp; &nbsp;  However, I wouldn't recommend using the script to protect your highly sensitive information for two reasons:
- the first is the algorithm it susceptible to <a href="https://daniellerch.me/stego/aletheia/lsbr-attack-en/">attacks on LSB replacement</a>
- the second is all the data is stored in plain text, in other words, the script encodes your data into an image but doesn't encrypt it in any way.

#### How it works:
&nbsp; &nbsp; &nbsp; &nbsp;  The script uses <a href="https://en.wikipedia.org/wiki/Bit_numbering#:~:text=In%20computing%2C%20the%20least%20significant,place%20of%20the%20binary%20integer.">the Least Significant Bit (LSB) </a> method to hide the message into an image which means it goes though all the pixels in the provided JPG file and changes the rightmost bits in every of them. Using JPG for the purpose is very convenient, since they don't have the alpha channel and use <a href="https://en.wikipedia.org/wiki/Endianness#:~:text=A%20big%2Dendian%20system%20stores,byte%20at%20the%20smallest%20address.">the big endian format</a> for encoding. 
 
##### Encoding data:
- We read the image  and transform it into <a href="https://www.mathworks.com/help/matlab/math/multidimensional-arrays.html">a multidimensional array:</a> 
	- Save the shape of the array
	- Transform the array into a one dimensional array
- Go though the message:
	- Clear all the LSB bits from the current subpixel using ***the mask_high_bits***  <a href="https://realpython.com/python-bitwise-operators/#bitwise-and">the bitwise AND operator</a>
	-  Extract ***the bits_per_color*** according to  ***the mask_low_bits*** using <a href="https://realpython.com/python-bitwise-operators/#bitwise-and">the bitwise AND operator</a>
	- Put them in a place from right to left using <a href="https://realpython.com/python-bitwise-operators/#right-shift">the right shift</a> and <a href="https://realpython.com/python-bitwise-operators/#bitwise-or">the bitwise OR operator</a> accordingly
- Reshape the array to its original form
- Save PNG file
```python
file_extension(image_path, EXTENSIONS)  
arr_img = convert_to_array(image_path)  
image = Image.fromarray(add_to_array(image=arr_img, msg=message)).convert("RGB")  
name = os.path.splitext(image_path)  
new_name = name[0] + "_ENCODED" + EXPORT_EXT  
image.save(new_name)  
image.show(new_name)  
print(f"Your message was successfully put into {new_name}. Congratulations!!!")
```

##### Extracting data:
- We read the image  
- Transform the image into a one dimensional array
- Go though the array
	- Read the chunks of data in the right-to-left order extracting one symbol per chunk. 
	- The script as long as it doesn't encounter an unprintable symbol
- Show the message
```python 
image = convert_to_array(image_path)  
print("Your encoded message is: ", read_from_array(image))
```



