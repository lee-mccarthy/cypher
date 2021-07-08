from __future__ import annotations


class BES:

    def __init__(self, keys: list[str]) -> None:
        if not all(map(lambda x: len(x) == 2, keys)):
            raise ValueError("All key strings must be of length 2.")
        self.keys = keys
        self.key_blocks = self.create_blocks(''.join(self.keys))

    @staticmethod
    def create_blocks(text: str) -> list[Block]:
        blocks = []
        for i in range(len(text)//2):
            blocks.append(BES.Block(text[i*2:i*2+2]))
        if len(text)%2 == 1:
            blocks.append(BES.Block(text[-1]))
        return blocks

    def encrypt(self, plaintext: str) -> str:
        text_blocks = self.create_blocks(plaintext)
        for key_block in self.key_blocks:
            key_block.swap_columns()
            for text_block in text_blocks:
                text_block.swap_columns()
                text_block.apply_xor(key_block)
                text_block.shift_rows_right()
            key_block.swap_columns()
        return ''.join(str(block) for block in text_blocks)

    def decrypt(self, ciphertext: str) -> str:
        text_blocks = self.create_blocks(ciphertext)
        for key_block in self.key_blocks[::-1]:
            key_block.swap_columns()
            for text_block in text_blocks:
                text_block.shift_rows_left()
                text_block.apply_xor(key_block)
                text_block.swap_columns()
            key_block.swap_columns()
        return ''.join(str(block) for block in text_blocks)

    def __repr__(self) -> str:
        return str(self.keys)

    class Block:

        def __init__(self, text: str) -> None:
            binaries = [str(bin(ord(letter)))[2:] for letter in text]
            for i in range(len(binaries)):
                binaries[i] = '0'*(8-len(binaries[i]))+binaries[i]
            binary = ''.join(binaries)
            self.block = []
            for i in range(len(binary)//4):
                self.block.append([])
                for j in range(4):
                    self.block[-1].append(int(binary[i*4+j]))
            if len(self.block) == 2:
                self.block.extend([[0, 0, 0, 0], [0, 0, 0, 0]])

        def swap_columns(self) -> None:
            for row in self.block:
                for i in range(2):
                    row[i*2], row[i*2+1] = row[i*2+1], row[i*2]

        def apply_xor(self, key: Block) -> None:  # type: ignore
            for i in range(len(self.block)):
                for j in range(len(self.block[i])):
                    self.block[i][j] ^= key.block[i][j]

        def shift_rows_right(self) -> None:
            shifted_block = []
            for i in range(4):
                shifted_block.append([])
                for j in range(4):
                    shifted_block[-1].append(self.block[i][(j-i)%4])
            self.block = shifted_block

        def shift_rows_left(self) -> None:
            shifted_block = []
            for i in range(4):
                shifted_block.append([])
                for j in range(4):
                    shifted_block[-1].append(self.block[i][(j+i)%4])
            self.block = shifted_block

        def __str__(self) -> str:
            digits = []
            for i in range(4):
                for j in range(4):
                    digits.append(str(self.block[i][j]))
            if all(map(lambda x: x == '0', digits[8:])):
                return chr(int(''.join(digits[:8]), 2))
            return chr(int(''.join(digits[:8]), 2))+chr(int(''.join(digits[8:]), 2))


class Enigma:

    def __init__(self) -> None:
        self.plugboard = self.Plugboard('')
        self.wheels = []
        self.reflector = None

    def set_plugboard(self, pairs: str) -> None:
        self.plugboard = self.Plugboard(pairs)

    def add_wheel(self, scramble: str, notches: set={0}, offset: int=0) -> None:
        self.wheels.append(self.Wheel(scramble, notches, offset))

    def set_reflector(self, scramble: str) -> None:
        self.reflector = self.Reflector(scramble)

    def engage(self, text: str) -> str:
        if not self.reflector:
            raise ValueError("The enigma machine must at least have a reflector. Create one with set_reflector().")
        text = ''.join(text.upper().split())
        if not text.isalpha():
            raise ValueError("All characters in the 'text' string must be alphabets or space.")
        starting_positions = [wheel.offset for wheel in self.wheels]
        new_text = []
        for letter in text:
            self.progress_wheels()
            new_letter = self.plugboard.engage(letter)
            index = ord(new_letter)-ord('A')
            for wheel in self.wheels:
                index = wheel.engage_forward(index)
            index = self.reflector.engage(index)
            for wheel in self.wheels[::-1]:
                index = wheel.engage_backward(index)
            new_letter = chr(ord('A')+index)
            new_letter = self.plugboard.engage(new_letter)
            new_text.append(new_letter)
        for i in range(len(starting_positions)):
            self.wheels[i].offset = starting_positions[i]
        return ''.join(new_text)

    def progress_wheels(self) -> None:
        for wheel in self.wheels:
            if not wheel.progress_offset():
                break

    class Plugboard:

        def __init__(self, pairs: str) -> None:
            pairs = pairs.upper().split()
            if not all(map(lambda x: x.isalpha() and len(x) == 2, pairs)):
                raise ValueError("The 'pairs' string must contain pairs of alphabet characters separated by spaces. eg: 'AX BY CZ'")
            self.pairs = {pair[0]: pair[1] for pair in pairs}
            self.pairs.update({pair[1]: pair[0] for pair in pairs})
            if len(self.pairs) != 2*len(pairs):
                raise ValueError("All characters in the 'pairs' string must be unique.")

        def engage(self, letter: str) -> str:
            return self.pairs.get(letter, letter)

    class Wheel:

        def __init__(self, scramble: str, notches: set, offset: int) -> None:
            if not scramble.isalpha():
                raise ValueError("All characters in the 'scramble' string must be alphabets.")
            self.scramble = scramble.upper()
            self.scrambled_indicies = {self.scramble[i]: i for i in range(len(self.scramble))}
            if len(self.scramble) != 26 or len(self.scrambled_indicies) != 26:
                raise ValueError("The 'scramble' string must contain all 26 alphabet characters exactly once each in any order.")
            if not all(map(lambda x: 0 <= x <= 25, notches)):
                raise ValueError("All notches must be in the range of 0 to 25 inclusive.")
            self.notches = notches
            if not (0 <= offset <= 25):
                raise ValueError("The offset must be in the range of 0 to 25 inclusive.")
            self.offset = offset

        def progress_offset(self) -> None:
            self.offset += 1
            self.offset %= 26
            return self.offset in self.notches

        def engage_forward(self, index: int) -> int:
            index += self.offset
            index %= 26
            letter = chr(ord('A')+index)
            new_index = self.scrambled_indicies[letter]
            new_index -= self.offset
            new_index %= 26
            return new_index

        def engage_backward(self, index: int) -> int:
            index += self.offset
            index %= 26
            letter = self.scramble[index]
            new_index = ord(letter)-ord('A')
            new_index -= self.offset
            new_index %= 26
            return new_index

    class Reflector:

        def __init__(self, scramble: str) -> None:
            if not scramble.isalpha():
                raise ValueError("All characters in the 'scramble' string must be alphabets.")
            self.scramble = scramble.upper()
            self.scrambled_indicies = {self.scramble[i]: i for i in range(len(self.scramble))}
            if len(self.scramble) != 26 or len(self.scrambled_indicies) != 26:
                raise ValueError("The 'scramble' string must contain all 26 alphabet characters exactly once each in any order.")

        def engage(self, index: int) -> int:
            letter = chr(ord('A')+index)
            new_index = self.scrambled_indicies[letter]
            return new_index


class Polybius:

    def __init__(self, key: str='') -> None:
        self.square = self.create_square(key)
        self.coordinates = self.set_coordinates(self.square)
        self.coordinates['J'] = self.coordinates['I']

    @staticmethod
    def create_square(key: str) -> list[list[str]]:
        for letter in key:
            if not letter.isalpha() and letter != ' ':
                raise ValueError("All characters in 'key' must be alphabets or a space character.")
        key = key.upper()
        square = [[]]
        redundant = {' '}
        for letter in key:
            if letter in redundant:
                continue
            if len(square[-1]) == 5:
                square.append([])
            if letter in 'IJ':
                square[-1].append('I')
                redundant.add('I')
                redundant.add('J')
            else:
                square[-1].append(letter)
                redundant.add(letter)
        for i in range(ord('A'), ord('Z')+1):
            letter = chr(i)
            if letter in redundant:
                continue
            if len(square[-1]) == 5:
                square.append([])
            if letter in 'IJ':
                square[-1].append('I')
                redundant.add('I')
                redundant.add('J')
            else:
                square[-1].append(letter)
                redundant.add(letter)
        return square

    @staticmethod
    def set_coordinates(square: list[list[str]]) -> dict[str, tuple[int]]:
        coords = dict()
        for i in range(5):
            for j in range(5):
                coords[square[i][j]] = (i+1, j+1)
        return coords

    def define_square(self, square: list[list[str]]) -> None:
        if len(square) != 5:
            raise ValueError("The input square must be a 5x5 grid.")
        for row in square:
            if len(row) != 5:
                raise ValueError("The input square must be a 5x5 grid.")
            for entry in row:
                if type(entry) is not str or len(entry) != 1:
                    raise ValueError("Each entry on the square must be a string of length 1.")
        self.square = [row.copy() for row in square]
        self.coordinates = self.set_coordinates(self.square)

    def encrypt(self, plaintext: str, reverse: bool=False) -> str:
        for letter in plaintext:
            if not letter.isalpha() and letter != ' ':
                raise ValueError("All characters in 'key' must be alphabets or a space character.")
        plaintext = plaintext.upper()
        cipher = []
        if reverse:
            for letter in plaintext:
                if letter == ' ':
                    continue
                cipher.append(str(self.coordinates[letter][1])+str(self.coordinates[letter][0]))
        else:
            for letter in plaintext:
                if letter == ' ':
                    continue
                cipher.append(str(self.coordinates[letter][0])+str(self.coordinates[letter][1]))
        return ' '.join(cipher)

    def decrypt(self, cipher: str, reverse: bool=False) -> str:
        letters = cipher.split(' ')
        for letter in letters:
            if len(letter) != 2 or letter[0] not in '12345' or letter[1] not in '12345':
                raise ValueError("The cipher must consist of 2-digit pairs in the range 1 to 5 inclusive, separated by spaces. eg: '31 42 53 32 51 24'")
        plaintext = []
        if reverse:
            for letter in letters:
                plaintext.append(self.square[int(letter[1])-1][int(letter[0])-1])
        else:
            for letter in letters:
                plaintext.append(self.square[int(letter[0])-1][int(letter[1])-1])
        return ''.join(plaintext)

    def __repr__(self) -> str:
        response = []
        for line in self.square:
            response.append(' '.join(line)+'\n')
        return ''.join(response)


class Vigenere:

    def __init__(self, key: str) -> None:
        if not key.isalpha():
            raise ValueError("All characters in 'key' must be alphabets.")
        self.key = key.upper()

    def encrypt(self, plaintext: str) -> str:
        if not plaintext.isalpha():
            raise ValueError("All characters in 'plaintext' must be alphabets.")
        plaintext = plaintext.upper()
        ciphertext = []
        for i in range(len(plaintext)):
            shift = ord(self.key[i%len(self.key)])-ord('A')+1
            ciphertext.append(chr((ord(plaintext[i])-ord('A')+shift)%26+ord('A')))
        return ''.join(ciphertext)

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext.isalpha():
            raise ValueError("All characters in 'plaintext' must be alphabets.")
        ciphertext = ciphertext.upper()
        plaintext = []
        for i in range(len(ciphertext)):
            shift = ord(self.key[i%len(self.key)])-ord('A')+1
            plaintext.append(chr((ord(ciphertext[i])-ord('A')-shift)%26+ord('A')))
        return ''.join(plaintext)

    def __repr__(self) -> str:
        return self.key
