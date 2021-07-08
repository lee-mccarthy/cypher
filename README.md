# cypher
The file 'cypher.ipynb' is a collection of my solutions to several of the
ciphers in the video game [Cypher by Matthew Brown](https://store.steampowered.com/app/746710/Cypher/).
Some of these solutions use the classes defined in 'cypher.py'.

The file 'cypher.py' contains classes for constructing various cipher keys. The
concept is that objects are cipher keys with methods that can be called to do
the following:

- Define the structure of the key
- Convert plaintext into ciphertext
- Convert ciphertext into plaintext

The ciphers available in this module are:

- Basic Encryption Standard (BES)
    - A simplified version of the Advanced Encryption Standard (AES)
    that is used to encrypt much information today, including a large portion
    of internet traffic. <https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>
- Enigma Machine
    - The infamous Enigma machine that was used by Nazi Germany to encrypt
    messages in the Second World War. It was an impressive feat of engineering
    that was also impressively cracked by Polish mathematicians and
    cryptanylists. The cracks in combination with information from Allied spies
    allowed the Allies to decipher Nazi military messages, which greatly
    influenced the direction of the war. <https://en.wikipedia.org/wiki/Enigma_machine>
- Polybius Square
    - A cipher that maps the letters of the alphabet to a two-dimensional grid.
    The grid is the key, and messages are encrypted as (X, Y) coordinates on the
    grid. <https://en.wikipedia.org/wiki/Polybius_square>
- Viginère Cipher
    - Essentially a Caesar cipher with extra steps, the Viginère cipher
    substitutes letters in a message with letters a certain number of steps
    further down the alphabet, looping back to the top of the alphabet if the
    bottom is reached. In a Caesar cipher, the number of steps to move is
    determined by a letter, with A meaning 1 step, and B meaning 2 steps, all
    the way down to Z meaning 26 steps, or a complete rotation of the alphabet.
    In a Viginère cipher, the number of steps is determined by a keyword. Start
    with the first letter in the keyword as a Caesar cipher, then for every
    letter moved across in the message, move across one letter in the keyword
    as a new Caesar cipher. When the keyword runs out of letters, move back to
    the beginning of it. <https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher>
