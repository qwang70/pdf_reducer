import difflib
import glob
import sys
import argparse
from PyPDF2 import PdfFileWriter, PdfFileReader

def createFile(fp):
    try:
        f = open(fp)
    except IOError as e:
        print "I/O error: Please input an existing pdf file"
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    PDF = PdfFileReader(file(fp, 'rb'))
    output = PdfFileWriter()

    rtn = []
    idx = PDF.getNumPages()-1
    prev = ""
    for i in range(PDF.getNumPages()-1,-1,-1):
        page = PDF.getPage(i)
        curr =  page.extractText()
        if len(curr)>len(prev):
            length = len(prev)
        else:
            length = len(curr)

        seq=difflib.SequenceMatcher(lambda x: x == " ",
                curr[0:length], prev[0:length])
        ratio = seq.ratio()
        if(ratio<0.8):
            rtn.append(idx)
            idx = i
        prev = curr
    if 0 not in rtn:
        rtn.append(0)
    #print rtn 

    rtn.reverse()
    for i in rtn:
        p = PDF.getPage(i)
        output.addPage(p)

    newfile = fp[0:-4]+"_reduced.pdf"
    with open(newfile, 'wb') as f:
       output.write(f)

def main():
    parser = argparse.ArgumentParser(description='Reduce duplicated PDF pages')
    parser.add_argument('String', metavar='pdf_filename', type=str, nargs='+',
                    help='PDF files to be reduced')
    args = parser.parse_args()
    files = []
    for i in sys.argv[1:]:
        files = files + glob.glob(i)

    for a_file in files:
        createFile(a_file);

if __name__ == '__main__':
    main()

