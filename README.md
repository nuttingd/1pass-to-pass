# 1pass-to-pass

A tool to migrate data from 1Password to password-store.

### Quick Start

This uses `pass insert ...` under the hood, so it will merge / overwrite items in your `.password-store`.

- Initialize password-store using your GPG key, if applicable
  ```shell
  pass init $KEYID
  ```
  
- Authenticate to 1Password in the current shell
  ```shell
  eval $(op signin)
  ```
  
- Run it
  ```shell
  python main.py
  ```

### `.password-store` Folder Structure

```
logins/www.example.com/smithj@example.com
```

### TODO
The import script doesn't do well with some item types, i.e. `Credit Cards`, `Bank Accounts`, etc.
