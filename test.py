import pypandoc
import os

fn = 'uploads/8c7dd922ad47494fc02c388e12c00eac.docx';
outputpath = outputfile=fn+'.pdf'
pypandoc.convert_file(fn, 'latex', outputfile=outputpath, extra_args=[])