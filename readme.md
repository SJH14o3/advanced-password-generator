## Advanced Password Generator
this app generates random password. generated password can with the length defined by user and contains digits, lowercase and uppercase alphabets and punctuations which the weight of them can be adjusted by user.
after generating a password, it will be encrypted using AES algorithm. program will show the user the generated and encrypted password using AES algorithm.
upon first run, a random key will be generated.
passwords can be decrypted but make sure the password to be encrypted was generated with the current stored key.
after generating a password, the config.json will be updated with the new configurations so upon next run, the previous configuration is loaded.