# plucker

given
blah/1/frame.jpg, blah/2/frame.jpg
and
bloo/1/mask.jpg, blah/2/mask.jpg

we might want them zipped together to
blah/1/frame.jpg & blah/1/mask.jpg

blah would be your basedir and bloo would be your fromdir.

flat just means they dont have subdirectories, its more like
blah/1.jpg needs bloo/1.jpg
to become
blah/1.jpg and blah/1_mask.jpg

that would be in flat mode, use the dest_fn_template to add _mask.

I needed this for something.

```
usage: plucker.py [-h] [--verbose] [--dry_run] [--key_template KEY_TEMPLATE] --basedir BASEDIR [--basedir_flat] --fromdir FROMDIR [--fromdir_flat] [--dest_fn_template DEST_FN_TEMPLATE] [--ignore_missing] [--force_overwrite]

options:
  -h, --help            show this help message and exit
  --verbose
  --dry_run             dont actually do any copying, use for testing
  --key_template KEY_TEMPLATE
                        override formatting of the key we will read from basedir and then search for in finddir. access {key} for existing value, e.g. we might do '{key}_mask' or even 'mask.png', depending on our pluckdir structure. file extension optional
  --basedir BASEDIR     target directory, we will pluck files INTO here. either a folder of subfolders (default) in which case each subfolder is the key, or a flat directory in which case each filename is a key
  --basedir_flat        basedir is 'flat', i.e. basedir/001.png, basedir/002.png, NOT subfolders
  --fromdir FROMDIR     pluck from this directory, should either a directory of subdirectories where the subdirectory matches our key (default), or a flat folder where the filenames match our key
  --fromdir_flat        fromdir is 'flat', a single folder with files inside it
  --dest_fn_template DEST_FN_TEMPLATE
                        template for filename we'll write back into basedir, can access template vars 'key' (pluck base key name) and ext (file extension of plucked file), uses python format(). e.g. '{key}.{ext}' is default behaviour, but maybe do '{key}_mask.{ext} if we're trying
                        to pluck a mask
  --ignore_missing      ignore missing plucks, i.e. allow a sparse job that only populates what it can find
  --force_overwrite     enable plucking that overwrites an existing file. be very very careful!
```
