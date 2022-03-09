#
# purge old files

import bash
import pandas
import json
import datetime
from typing import Optional
import typer
import time

def main(bucket_name:str,
         folder_name: Optional[str] = typer.Argument(""),
         keep_days:int=366,
         dry_run:bool=False,
         recursive:bool=True):
    # use the b2 command line tool
    # list the bucket including all versions
    if recursive:
        output = bash.bash_silent(f"b2 ls {bucket_name} {folder_name} --versions --json --recursive ")
    else:
        output = bash.bash_silent(f"b2 ls {bucket_name} {folder_name} --versions --json")
    #print(output)
    #df = pandas.DataFrame([x.split(" ") for x in output.split('\n')])
    data = json.loads(output)
    #print(json.dumps(data, indent=2))
    # assemble a list of all files

    # loop through the files that have a date string appended (careful to not match within the actual file name)
    # make sure they also have a matching version of the file more recent than the date.
    
    # find all files that are before the date

    keep_before = datetime.datetime.now() - datetime.timedelta(days=keep_days)
    print(f'keep_before: {type(keep_before)}')
    print(f'keep_before: {format_dt(keep_before)}')
    #time.sleep(1)

    # collect the latest version of each file that must be saved.
    # as a dictionary of filenames
    latest_versions = {}
    i = 0
    for d in data:
        filename = d["fileName"]
        ts1 = d["uploadTimestamp"]
        dt1 = datetime.datetime.utcfromtimestamp(ts1 / 1000)

        if filename in latest_versions:
            ts2 = latest_versions[filename]["uploadTimestamp"]
            dt2 = datetime.datetime.utcfromtimestamp(ts2 / 1000)
            if dt1 > dt2:
                # find latest version of each file
                print(f"updating {filename} to {dt1}")
                latest_versions[filename] = d
            else:
                print(f"no update to {filename}, {dt2} newer than {dt1}")
        else:
            # first version of this filename
            print(f"adding initial version of {filename}, {dt1}")
            latest_versions[filename] = d

        # debug a particular problem:
        #if d["fileName"] == "hints.10026":
        #    print(json.dumps(d,indent=2))
        #    time.sleep(2)
        #if i < 4:
        #    print(json.dumps(d,indent=2))
        #    time.sleep(0.1)
        i += 1


#    latest_non_hidden = {}
#    # exclude hidden files, because if they are marked hidden, even the latest can be removed.
#    for key, value in latest_versions.items():
#        print(json.dumps(value,indent=2))
#        if (value["action"] == "hide") and (value["contentType"] == "application/x-bz-hide-marker"):
#            continue
#        else:
#            latest_non_hidden[key] = value

    # loop through the full list (data) and build up a list excluding all of the latest files.
    # do not exclude latest files if they are hidden
    old_files = []
    for d in data:
        filename = d["fileName"]
        ts1 = d["uploadTimestamp"]
        ts2 = latest_versions[filename]["uploadTimestamp"]
        # if this is not the latest, it can be potentially purged
        if ts1 != ts2:
            old_files.append(d)
        elif (latest_versions[filename]["action"] == "hide") and (latest_versions[filename]["contentType"] == "application/x-bz-hide-marker"):
            # if the latest file is hidden, even it can be potentially purged        
            old_files.append(d)


    total_n = len(data)
    old_file_n = len(old_files)
    print(f"{old_file_n} old files available to purge")

    to_delete = []

    for d in old_files:
        if d["fileName"] == "hints.10026":
            print(json.dumps(d,indent=2))
        ts1 = d["uploadTimestamp"]
        dt1 = datetime.datetime.utcfromtimestamp(ts1 / 1000)

        #ts2 = int(d["fileInfo"]["src_last_modified_millis"])
        #dt2 = datetime.datetime.utcfromtimestamp(ts2 / 1000)
        #print(timestamp_display(ts2))
        #print(ts2)
        
        if dt1 < keep_before:
            #print(ts1)
            tsd1 = timestamp_display(ts1)
            tsd2 = format_dt(keep_before)
            print(f"will delete {d['fileName']} {d['fileId']} {tsd1} older than {tsd2}")
            to_delete.append(d)

    n = len(to_delete)

    size = 0
    for d in to_delete:
        size = size+d['size']
    
    print(f"about to delete {n} files out of {old_file_n} old files out of {total_n} total files")
    print(f"about to delete {size:,} bytes")

    # delay a bit in case the user sees something wrong they can ctrl c out.
    time.sleep(2)
    # if dryRun stop here.
    if dry_run:
        print("dry run... nothing deleted.")
        return
    
    # compare to see if it is within keep days
    # if not, add the filename and fileid to the delete list
    # print the list

    # loop through the list of files to delete
    for d in to_delete:
        # actually delete the files using
        # b2 delete-file-version fileName fileId
        b2_delete(d)


def b2_delete(d):
    # actually delete the files using
    # b2 delete-file-version fileName fileId
    fileName = d["fileName"]
    fileId = d["fileId"]
    bash.bash(f'b2 delete-file-version {fileName} {fileId}')


# https://github.com/Backblaze/B2_Command_Line_Tool/blob/master/b2/console_tool.py
def timestamp_display(timestamp_or_none):
    """
    Returns a pair (date_str, time_str) for the given timestamp
    """
    if timestamp_or_none is None:
        return '-'
    else:
        timestamp = timestamp_or_none
        dt = datetime.datetime.utcfromtimestamp(timestamp / 1000)
        return format_dt(dt)


def format_dt(dt):
    return(dt.strftime('%Y-%m-%d %H:%M:%S.%f'))


if __name__ == '__main__':
    typer.run(main)
