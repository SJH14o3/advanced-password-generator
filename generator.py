import tkinter as tk
import random
import string
import json
import os
import pyperclip
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

CONFIG_FILE = "config.json"
generated_password = None
generated_password_encrypted = None

# Padding for the input string
BLOCK_SIZE = 16

def pad(s):
    # Pad with spaces to make the string a multiple of BLOCK_SIZE
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

def unpad(s):
    # Remove the padding from the string
    return s[:-ord(s[len(s) - 1:])]

# Function to generate a random encryption key
def generate_key():
    key = get_random_bytes(16)  # 16 bytes = 128 bits key
    with open("aes.key", "wb") as key_file:
        key_file.write(key)

# Function to load the encryption key from a file
def load_key():
    with open("aes.key", "rb") as key_file:
        key = key_file.read()
    return key

# Function to encrypt a password
def encrypt_password(password):
    key = load_key()
    cipher = AES.new(key, AES.MODE_CBC)  # Create a new AES cipher
    iv = cipher.iv  # Initialization vector
    encrypted_password = cipher.encrypt(pad(password).encode())  # Encrypt the padded password
    encrypted_password_with_iv = iv + encrypted_password  # Prepend the IV for decryption
    return base64.b64encode(encrypted_password_with_iv).decode()  # Encode as base64 for easy storage

# Function to decrypt a password
def decrypt_password(encrypted_password):
    key = load_key()
    encrypted_password_with_iv = base64.b64decode(encrypted_password)
    iv = encrypted_password_with_iv[:16]  # Extract the IV from the beginning
    encrypted_password = encrypted_password_with_iv[16:]  # The actual encrypted password
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_password = unpad(cipher.decrypt(encrypted_password).decode())
    return decrypted_password

# Function to load configuration from a JSON file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    # Return default configuration if file doesn't exist
    return {
        "length": 12,
        "lower_weight": 1,
        "upper_weight": 1,
        "digit_weight": 1,
        "special_weight": 1
    }

def decrypt_password_action():
    if decrypt_entry is None:
        decrypted_password_label.config(text="No password to decrypt.")
        return
    try:
        
        # Decrypt the encrypted password
        decrypted_password = decrypt_password(generated_password_encrypted)
        
        # Update the decrypted password label to show the decrypted password
        decrypted_password_label.config(text="Decrypted Password: " + decrypted_password)
    
    except Exception as e:
        # If there's an error (e.g., Base64 decoding fails, wrong key), show an error message
        decrypted_password_label.config(text="Error decrypting password: " + str(e))



# Function to save configuration to a JSON file
def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# Function to generate a random password based on user input
def generate_password():
    # Get user inputs
    length = int(length_entry.get())
    lower_weight = int(lower_weight_entry.get())
    upper_weight = int(upper_weight_entry.get())
    digit_weight = int(digit_weight_entry.get())
    special_weight = int(special_weight_entry.get())
    
    # Save the current configuration
    config = {
        "length": length,
        "lower_weight": lower_weight,
        "upper_weight": upper_weight,
        "digit_weight": digit_weight,
        "special_weight": special_weight
    }
    sumWeight = lower_weight + upper_weight + digit_weight + special_weight
    if (sumWeight == 0):
        password_label.config(text="Please set weights greater than zero.")
        return
    
    save_config(config)
    # Create pools of characters with specified weights
    passwordList = []
    for _ in range(length):
        rng = random.randint(0, sumWeight)
        print()
        if (rng <= lower_weight):
            passwordList.append(random.choice(string.ascii_lowercase))
        elif (rng <= lower_weight + upper_weight):
            passwordList.append(random.choice(string.ascii_uppercase))
        elif (rng <= lower_weight + upper_weight + digit_weight):
            passwordList.append(random.choice(string.digits))
        else:
            passwordList.append(random.choice(string.punctuation))
    # Generate the password
    password = ''.join(passwordList)
    global generated_password
    generated_password = password
    global generated_password_encrypted
    encrypted = encrypt_password(password)
    generated_password_encrypted = encrypted
    label = password + '\n' + str(encrypted)[2:-1]
    password_label.config(text=label)

def copy_plain_password():
    if not generated_password == None:
        pyperclip.copy(generated_password)

def copy_encrypted_password():
    if not generated_password_encrypted == None:
        pyperclip.copy(str(generated_password_encrypted[2:-1]))
    
# Load configuration at startup
config = load_config()
# if key file doesn't exist, generate a new key
if not os.path.exists("aes.key"):
    generate_key()
# Create the main window
window = tk.Tk()
window.title("Password Generator, Encryptor, and Decryptor")
window.geometry("1000x700")

# Input for password length
tk.Label(window, text="Password Length:").pack()
length_entry = tk.Entry(window)
length_entry.insert(0, str(config["length"]))
length_entry.pack()

# Input for lowercase weight
tk.Label(window, text="Lowercase Weight:").pack()
lower_weight_entry = tk.Entry(window)
lower_weight_entry.insert(0, str(config["lower_weight"]))
lower_weight_entry.pack()

# Input for uppercase weight
tk.Label(window, text="Uppercase Weight:").pack()
upper_weight_entry = tk.Entry(window)
upper_weight_entry.insert(0, str(config["upper_weight"]))
upper_weight_entry.pack()

# Input for digit weight
tk.Label(window, text="Digit Weight:").pack()
digit_weight_entry = tk.Entry(window)
digit_weight_entry.insert(0, str(config["digit_weight"]))
digit_weight_entry.pack()

# Input for special character weight
tk.Label(window, text="Special Character Weight:").pack()
special_weight_entry = tk.Entry(window)
special_weight_entry.insert(0, str(config["special_weight"]))
special_weight_entry.pack()

# Create a label to display the generated password
password_label = tk.Label(window, text="Click the button to generate a password", wraplength=950, padx=10, pady=20)
password_label.pack(pady=20)

# Create a button to generate the password
generate_button = tk.Button(window, text="Generate Password", command=generate_password)
generate_button.pack()

# input for decrypting
tk.Label(window, text="Insert password to decrypt:").pack()
decrypt_entry = tk.Entry(window, width=130)
decrypt_entry.pack()

# Create a button to decrypt inserted password
decrypt_button = tk.Button(window, text="Decrypt Password", command=decrypt_password_action)
decrypt_button.pack(pady=10)

decrypted_password_label = tk.Label(window, text="Decrypted Password: ")
decrypted_password_label.pack(pady=5)

copy_plain_password_button = tk.Button(window, text="copy plain password", command=copy_plain_password)
copy_plain_password_button.pack(pady=10)

copy_encrypted_password_button = tk.Button(window, text="copy encrypted password", command=copy_encrypted_password)
copy_encrypted_password_button.pack(pady=10)

# Run the application
window.mainloop()
