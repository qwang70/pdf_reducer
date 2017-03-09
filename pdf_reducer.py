import difflib
import glob
import sys
import argparse
from io import FileIO as file
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import itertools
import tarfile

def ranges(i):
    for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
        b = list(b)
        yield b[0][1], b[-1][1]+1

def reduceMergeFile(files):
    """
        input:
        files: a list of file to be reduced and merged
    """
    reduced_filenames = reduceFile(files, 0)
    mergeFile(reduced_filenames)

def reduceMergeFile2(files):
    """
        input:
        files: a list of file to be reduced and merged
    """
    openfile = map(lambda x: file(x, 'rb'), files)
    keepPages = reduceFile(files, False)

    pageRages = map(lambda x: list(ranges(x)), keepPages)
    merger = PdfFileMerger()
    for i in range(len(keepPages)):
        print("Merging file \"{}\"...".format(files[i]))
        for pageRage in pageRages[i]:
            merger.append(fileobj = openfile[i], pages=pageRage)

    newfile = "reduced_and_merged.pdf"
    with open(newfile, 'wb') as f:
        merger.write(f)

def mergeFile(files):
    """
        input:
        files: a list of file to merge
    """
    merger = PdfFileMerger()
    for f in files:
        print("Merging file \"{}\"...".format(f))
        # check if file can be opened
        try:
            # read and merge pdf with pypdf2
            merger.append(PdfFileReader(file(f, 'rb')))
        except IOError as e:
            print("I/O error: Please input an existing pdf file:", fp)
            raise
        except:
            print(fp, ": Unexpected error - ", sys.exc_info()[0])
            raise
    # TODO: need to change output path later
    merger.write("output/output.pdf")


def reduceFile(files, compress = True):
    """
        input:
        fp: a list of file to reduce
        return:
        keepPage: pages to keep
    """
    newfiles = []
    for fp in files:
        print("Reducing file \"{}\"...".format(fp))
        # check if file can be opened
        try:
                    # read pdf with pypdf2
            PDF = PdfFileReader(file(fp, 'rb'))
        except IOError as e:
            print("I/O error: Please input an existing pdf file:", fp)
            raise
        except:
            print(fp, ": Unexpected error - ", sys.exc_info()[0])
            raise
        output = PdfFileWriter()

        # keepPage is the page to be outputed
        keepPage = []
        idx = PDF.getNumPages() - 1
        prev = ""
        for i in range(PDF.getNumPages() - 1, -1, -1):
            page = PDF.getPage(i)
            curr = page.extractText()
            if not curr:
                if idx > i:
                    keepPage.append(idx)
                keepPage.append(i)
                idx = i - 1
                page = PDF.getPage(idx)
                prev = page.extractText()
                continue
            # set the page length of last idxed page
            if len(curr) > len(prev):
                length = len(prev)
            else:
                length = len(curr)
            # calculate the similarity btw last page and curr page
            seq = difflib.SequenceMatcher(lambda x: x == " ",
                                          curr[0:length], prev[0:length])
            ratio = seq.ratio()
            # print "page is {}, ratio is {}".format(i, ratio)
            # decision making, update index
            if ratio < 0.8:
                keepPage.append(idx)
                idx = i
            prev = curr
        if 0 not in keepPage:
            keepPage.append(0)
        # print keepPage

        # backward idx to forward idx
        keepPage.reverse()
        # add page numbers to output
        for i in keepPage:
            p = PDF.getPage(i)
            output.addPage(p)

        # TODO: need to change output path later
        # rename file
        newfile = fp[0:-4] + "_reduced.pdf"
        # add file into returned filename list
        newfiles.append(newfile)
        # write file into pdf
        with open(newfile, 'wb') as f:
            output.write(f)

    # compress file into a tar file
    if compress:
        with tarfile.open("reduced_files.tar", "w") as tar:
            for name in newfiles:
                tar.add(name)
    return newfiles

def main():
    # input checking and utility
    parser = argparse.ArgumentParser(description='Reduce duplicated PDF pages')
    parser.add_argument('-m', '--merge', action='store_true',
                        help='merge PDF files')
    parser.add_argument('-r', '--reduce', action='store_true',
                        help='reduce PDF file(s)')
    parser.add_argument('-rm', '--reduceMerge', action='store_true',
                        help='reduce PDF files, and merge them into one file')
    parser.add_argument('filenames', type=str, nargs='+',
                        help='PDF files to be reduced or merged')
    args = parser.parse_args()
    # list of files
    files = []
    for i in args.filenames:
        files = files + glob.glob(i)

    # merge
    if args.merge:
        mergeFile(files)
    elif args.reduceMerge:
        reduceMergeFile(files)
    else:
        reduceFile(files)

if __name__ == '__main__':
    main()
