import argparse
import glob
import os
import stat
import shutil

class GracefulSkip(Exception): pass

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--dry_run", action="store_true", help="dont actually do any copying, use for testing")
parser.add_argument("--key_template", default="{key}", help="override formatting of the key we will read from basedir and then search for in finddir. access {key} for existing value, e.g. we might do '{key}_mask' or even 'mask.png', depending on our pluckdir structure. file extension optional")
parser.add_argument("--basedir", required=True, help="target directory, we will pluck files INTO here. either a folder of subfolders (default) in which case each subfolder is the key, or a flat directory in which case each filename is a key")
parser.add_argument("--basedir_flat", action="store_true", help="basedir is 'flat', i.e. basedir/001.png, basedir/002.png, NOT subfolders")
parser.add_argument("--fromdir", required=True, help="pluck from this directory, should either a directory of subdirectories where the subdirectory matches our key (default), or a flat folder where the filenames match our key")
parser.add_argument("--fromdir_flat", action="store_true", help="fromdir is 'flat', a single folder with files inside it")
parser.add_argument("--dest_fn_template", default="{key}.{ext}", help="template for filename we'll write back into basedir, can access template vars 'key' (pluck base key name) and ext (file extension of plucked file), uses python format(). e.g. '{key}.{ext}' is default behaviour, but maybe do '{key}_mask.{ext} if we're trying to pluck a mask")
parser.add_argument("--ignore_missing", action="store_true", default=False, help="ignore missing plucks, i.e. allow a sparse job that only populates what it can find")
parser.add_argument("--force_overwrite", action="store_true", default=False, help="enable plucking that overwrites an existing file. be very very careful!")
args = parser.parse_args()


def raise_exc_dest_exists(dest, force=False):
    try:
        os.stat(dest_path)
        if not force:
            raise ValueError("will not pluck to already existing path: %s, considering using --dest_fn_template to give it a unique suffix or smth. or --force_overwrite if you are a cowboy" % (dest_path))
    except FileNotFoundError:
        pass

def prep_pluck(pdir, key, ignore_missing=False):

    pglob = pdir + "/" + key + ".*"
    print("plucking from %s with key %s using glob '%s'" % (pdir, key, pglob))

    pluckees = glob.glob(pglob)

    if len(pluckees) == 0 and not ignore_missing:
        raise FileNotFoundError("found no files for key %s in dir %s " % (key, pdir))
    if len(pluckees) == 0 and args.ignore_missing:
        print("gracefully skipping missing pluck for key %s, due to ignore_missing=True" % (key))
        raise GracefulSkip()
    if len(pluckees) > 1:
        raise ValueError("key %s expected exactly 1 pluckee, got %s" % (key, pluckees))

    pluckee = pluckees[0]
    _, ext = os.path.splitext(pluckee)
    ext = ext[1:]

    return pluckee, ext

if args.basedir_flat:
    print("running for basedir %s in with flat=%s" % (args.basedir, args.basedir_flat))
    basedir_files = glob.glob(args.basedir + "/*")
        
    # filter out directories
    basedir_files = list(filter(lambda f: not stat.S_ISDIR(os.lstat(f).st_mode), basedir_files))
    if len(basedir_files) == 0:
        raise ValueError("could not pluck into from basedir %s, is empty" % (args.basedir))

    for bdf in basedir_files:

        #mode = os.lstat(bdf).st_mode
        #if stat.S_ISDIR(mode):
        #    continue

        # original key (in basedir) and derived key (can be overriden to compensate for format of pluck dir)
        _, og_key = os.path.split(bdf)
        og_key, og_ext = os.path.splitext(og_key)
        der_key = args.key_template.format(key=og_key)
        if args.verbose:
            print(og_key + " is basedir key, using " + der_key + " as derived key")

        if args.fromdir_flat:
            fromdir = args.fromdir
        else:
            fromdir = args.fromdir + "/" + og_key

        try:
            pluckee, pluckee_ext = prep_pluck(fromdir, der_key, ignore_missing=args.ignore_missing)
        except FileNotFoundError:
            raise ValueError("could not find key '%s' in fromdir '%s', add --ignore_missing if this is ok" % (der_key, args.fromdir))
        except GracefulSkip:
            continue

        dest_fn = args.dest_fn_template.format(key=og_key, ext=pluckee_ext)
        dest_path = args.basedir + "/" + dest_fn

        if args.verbose:
            print("will pluck %s to destination %s" % (pluckee, dest_path))

        raise_exc_dest_exists(dest_path, args.force_overwrite)

        if args.dry_run:
            pass
        else:
            shutil.copyfile(pluckee, dest_path)


else:
    print("running for basedir %s in with flat=%s" % (args.basedir, args.basedir_flat))
    basedir_files = glob.glob(args.basedir + "/*")

    # filter for only directories
    basedir_files = list(filter(lambda f: stat.S_ISDIR(os.lstat(f).st_mode), basedir_files))
    if len(basedir_files) == 0:
        raise ValueError("could not pluck into from basedir %s, is empty" % (args.basedir))

        
    for bdf in basedir_files:

        # original key (in basedir) and derived key (can be overriden to compensate for format of pluck dir)
        _, og_key = os.path.split(bdf)
        der_key = args.key_template.format(key=og_key)
        if args.verbose:
            print(og_key + " is basedir subdirectory, using " + der_key + " as derived key")

        if args.fromdir_flat:
            fromdir = args.fromdir
        else:
            fromdir = args.fromdir + "/" + og_key


        try:
            pluckee, pluckee_ext = prep_pluck(fromdir, der_key, ignore_missing=args.ignore_missing)
        except FileNotFoundError:
            raise ValueError("could not find key '%s' in fromdir '%s', add --ignore_missing if this is ok" % (der_key, args.fromdir))
        except GracefulSkip:
            continue

        dest_fn = args.dest_fn_template.format(key=og_key, ext=pluckee_ext)
        dest_path = bdf + "/" + dest_fn

        print("will pluck %s to destination %s" % (pluckee, dest_path))
        raise_exc_dest_exists(dest_path)

        if args.dry_run:
            pass
        else:
            shutil.copyfile(pluckee, dest_path)
