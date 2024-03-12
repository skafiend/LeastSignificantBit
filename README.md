# LSB Steganography 
#### Video Demo:  <URL HERE>
#### Description:
This simple python script encodes your data using provided JPG image and converts the latter to PNG file with the encoded information. Those files are indistinguishable for the naked eye, and that gives us an opportunity not only hide the information itself, but also hide the fact that the data was transferred. However, I wouldn't recommend using the script to protect your highly sensitive information for two reasons.
The first is all the data is stored in plain text that makes it susceptible to <a href="https://daniellerch.me/stego/aletheia/lsbr-attack-en/">attacks on LSB replacement/</a>, and the second is the script encodes your data but doesn't encrypts it in any way.

