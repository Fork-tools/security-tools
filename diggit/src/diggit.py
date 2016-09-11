#!/usr/bin/python
#
# bl4de | <bloorq@gmail.com> | https://twitter.com/_bl4de
#
# diggit - gets .git repository
import argparse
import os
import re

# some common definitions
VERSION = "1.0.0"
OBJECT_DIR = "/.git/objects/"

Black = '\33[30m'
Red = '\33[31m'
Green = '\33[32m'
Yellow = '\33[33m'
Blue = '\33[34m'
Magenta = '\33[35m'
Cyan = '\33[36m'
White = '\33[37m'
_endline = '\33[0m'


def print_banner():
    """Prints credits :)"""
    print "\n\n", "#" * 78
    print "###", " " * 70, "###"
    print "###", " " * 70, "###"
    print "###         diggit.py  |  Twitter: @_bl4de  " \
          "| GitHub: bl4de                ###"
    print "###", " " * 70, "###"
    print "###", " " * 70, "###"
    print "#" * 78


def print_object_details(objtype, objcontent, objhash, objfilename):
    """Prints and saves object details/content"""
    save_file = False
    if objfilename != "":
        global localgitrepo
        tmpfp = localgitrepo + "/" + objfilename
        save_file = True

    print "\n" + Cyan + "#" * 12 + " " + objhash \
          + " information " + "#" * 12 + _endline
    print "\n{0}[*] Object type: {3}{2}{1}{3}".format(Green, objtype, Red,
                                                      _endline)

    if save_file:
        print "{0}[*] Object filename: {3}{2}{1}{3}".format(Green, objfilename,
                                                            Red, _endline)
        print "{0}[*] Object saved in {2}:{1}".format(Green, _endline,
                                                      tmpfp)

    print "{0}[*] Object content:{1}\n".format(Green, _endline)
    print "{0}{1}{2}".format(Yellow, objcontent, _endline)

    if save_file:
        tmpfile = open(tmpfp, "w")
        tmpfile.write("// diggit.py by @bl4de | {} content\n".format(objhash))
        tmpfile.writelines(objcontent)
        tmpfile.close()


def get_object_url(objhash):
    """Returns object git url"""
    return OBJECT_DIR + objhash[0:2] + "/" + objhash[2:]


def get_object_dir_prefix(objhash):
    """Returns object directory prefix (first two chars of object hash)"""
    return objhash[0:2] + "/"


def get_objhash_from_object_desc(gitobjcontent):
    """returns object hash without control characters"""
    return gitobjcontent.split(" ")[1][:40]


def save_git_object(baseurl, objhash, berecursive, objfilename=""):
    """Saves git object in temporary .git directory preserves its path"""
    finalurl = baseurl + "/" + get_object_url(objhash)

    os.system("curl --silent '" + finalurl + "' --create-dirs -o '" +
              localgitrepo + get_object_url(objhash) + "'")

    gitobjtype = os.popen("cd " + localgitrepo + OBJECT_DIR +
                               get_object_dir_prefix(objhash) +
                               " && git cat-file -t " + objhash).read()

    gitobjcontent = os.popen("cd " + localgitrepo + OBJECT_DIR +
                                  get_object_dir_prefix(objhash) +
                                  " && git cat-file -p " + objhash).read()
    print_object_details(gitobjtype, gitobjcontent, objhash,
                         objfilename)

    # get actual tree from commit
    if gitobjtype.strip() == "commit" and berecursive is True:
        save_git_object(baseurl,
                        get_objhash_from_object_desc(gitobjcontent),
                        berecursive)

    if gitobjtype.strip() == "tree" and berecursive is True:
        for obj in gitobjcontent.split("\n"):
            if obj:
                obj = obj.strip().split(" ")
                objhash = obj[2][:40]
                real_filename = obj[2].split("\t")[1]
                if objhash != "" and re.match(r"[a-zA-Z0-9]", objhash):
                    save_git_object(baseurl, objhash, berecursive,
                                    real_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
            diggit.py - get information about Git object(s) from remote
                        repository
        """)
    parser.add_argument('-u', help='URL of remote Git repository location')
    parser.add_argument('-t',
                        help='path to temporary Git folder on local machine')
    parser.add_argument('-o', help='object hash (SHA-1, all 40 characters)')
    parser.add_argument('-r', default=False,
                        help='be recursive (if commit or tree hash '
                             'found, go get all blobs too). Default is \'False\'')

    args = parser.parse_args()

    # domain, base path for .git folder, eg. http://website.com
    baseurl = args.u

    # hash of object to save
    objecthash = args.o
    berecursive = True if args.r else False

    # temporary dir with dummy .git structure (create it first!)
    localgitrepo = args.t

    if baseurl and objecthash:
        print_banner()
        save_git_object(args.u, args.o, berecursive, "")
        print "\n" + Cyan + "#" * 78 + _endline
