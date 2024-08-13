import os
import sys
import datetime
import pandas as pd

# Definição do dicionário Morse
dict_morse = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", 
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J", 
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O", 
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T", 
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y", 
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2", "...--": "3", 
    "....-": "4", ".....": "5", "-....": "6", "--...": "7", "---..": "8", 
    "----.": "9", "/": " "  # Espaço entre palavras
}

file_path = "decoded_messages.csv"

def decode_morse(msg):
    '''
    input : mensagem em código morse com as letras separadas por espaços
    output : palavra escrita em letras e algarismos
    '''
    # Divide a mensagem em palavras usando três espaços
    msg_lst = msg.split("   ")
    msg_claro = []
    for word in msg_lst:
        # Divide cada palavra em letras usando um espaço
        letters = word.split(" ")
        # Decodifica cada letra e adiciona à palavra decodificada
        decoded_word = ''.join([dict_morse.get(letter, '?') for letter in letters])
        msg_claro.append(decoded_word)
    # Une todas as palavras decodificadas
    return ' '.join(msg_claro)

def save_clear_msg_csv_hdr(msg_claro):
    '''
    input : mensagem em texto claro
    output : palavra escrita em letras e algarismos, salva em arquivo csv
    '''
    now = datetime.datetime.now()
    df = pd.DataFrame([[msg_claro, now]], columns=["mensagem", "datetime"])
    hdr = not os.path.exists(file_path)
    df.to_csv(file_path, mode="a", index=False, header=hdr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        morse_msg = sys.argv[1]
        msg_claro = decode_morse(morse_msg)
        save_clear_msg_csv_hdr(msg_claro)
        print(f"Mensagem decodificada: {msg_claro}")
    else:
        print("Por favor, forneça uma mensagem em código morse como argumento.")
