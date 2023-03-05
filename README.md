# Chaotic-Audio-Encryption

## About the project
A Python implementation of the chaos based, real time audio encryption method proposed in the paper:
""
which is submitted to the Conference:
MOCAST 2023

The implementation offers a GUI that allows the user to encrypt audio files based on the key that they select and save the encrypted message.
Additionally, it allows the user to select encrypted audio files and decrypt them, by selecting the appropriate keys.


## Getting Started
### Prerequisites
<ul>
<li> PyQt6 </li>
<li> pyaudio </li>
<li> numpy </li>
<li> scipy </li>
</ul>


### Instalation
Clone the repository

 ```
  https://github.com/iokaf/Chaotic-Audio-Encryption.git
  ```

Install the requirements
 ```
  pip install -r requirements.txt
  ```

Run the interface

 ```
  python main.py
  ```

## Usage
The implementation offers a GUI that allows the user to encrypt audio files based on the key that they select and save the encrypted message.
Additionally, it allows the user to select encrypted audio files and decrypt them, by selecting the appropriate keys.

More explicitly, for the encryption process, the user initially selects the directory where the encrypted audio file is to be saved and the filename to be used. 
This is done by pressing the **Select Save Directory** button.
The audio file is saved in wav form.

Subsequently, the user selects the initial condition and parameter value to be used, by pressing the **Select Encryption Keys** button.

Once this is done, the user can start a recording by pressing the **Start** 
button, which starts the recording and encryption process.
The prosses continues untill the user presses the **Stop** button, which stops the recording and writes the encrypted audio file.

To decrypt a saved audio file, the user initially selects the file to be decrypted by pressing the **Select Encrypted File** button.
Subsequently, the decryption keys to be used are selected by pressing the **Select Decryption Keys** button.
Next, the path and name for the decrypted audio file is selected using the **Select Decryption Save Directory** button.
Finally, pressing the **Decrypt** button initializes the decryption process and saved the decrypted file.

## Testing

The functionality of the implementation has been tested with 
Ubuntu 20.04 and an Intel i7 processor.
Additioanlly, it was tested with Windows 10 and an Intel i5 processor.
Still, bugs may exists. 
Please feel free to report a bug or request a feature.


## Limitations
Althougth the method has been tested and works with different Operational Systems and it works, messages encrypted with one architecture may fail to be decrypted in a different one, even if the same keys are selected, due to numerical differences.

## Licence
MIT License

Copyright (c) 2023 Dr. Ioannis Kafetzis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Contact


## Reference 
**Original Paper**

> title={Automata-Derived Chaotic Image Encryption Scheme}, <br>
> author={Kafetzis, Ioannis and Volos, Christos and 
> Nistazakis, Hector E. ænd
> Goudos, Sotirios
> booktitle={2023 12th International Conference on Modern Circuits and    Systems Technologies (MOCAST)}, <br>
> pages={1--4}, <br>
> year={2023}, <br>
> organization={IEEE}


Cite this repository

> @misc{kafetzis2023chaoticaudioencryption, <br>
  author = {Kafetzis, I.}, <br>
  title = {Chaotic Audio Encryption}, <br>
  year = {2023}, <br>
  publisher = {GitHub}, <br>
  journal = {GitHub repository}, <br>
  howpublished = {\url{https://github.com/iokaf/Chaotic-Audio-Encryption}}, <br>
 }
