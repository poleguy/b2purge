# b2purge
backblaze b2 command line tool to remove files older than n days.

```
Usage: b2purge.py [OPTIONS] BUCKET_NAME [FOLDER_NAME]

Arguments:
  BUCKET_NAME    [required]
  [FOLDER_NAME]  [default: ]

Options:
  --keep-days INTEGER             [default: 366]
  --dry-run / --no-dry-run        [default: no-dry-run]
  --recursive / --no-recursive    [default: recursive]
  --help                          Show this message and exit.
```

to use:

source ./setup_python

python b2purge.py bucket-name path/to/limit --dry-run --keep-days 180