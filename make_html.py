#!/usr/bin/env python

import os
import fnmatch
import sys
import time
import relpath #user defined as Python versions before 2.6 dont have this built in - sigh!
from optparse import OptionParser

# parse options
parser = OptionParser(usage="usage: %prog dirname [options]")
parser.add_option("-t","--sortByTime",action="store_true",dest="sortbytime",default=False,help="Sort plots by date modified")
parser.add_option("-k","--sortByType",action="store_true",dest="sortbytype",default=False,help="Sort plots by file type")
parser.add_option("-c","--contents",action="store_true",dest="contents",default=False,help="Display table of contents on each page")
parser.add_option("-l","--links",action="store_true",dest="links",default=False,help="Add links")
parser.add_option("-n","--notes",action="store_true",dest="notes",default=False,help="Show notes")
parser.add_option("-e","--expandText",action="store_true",dest="expandText",default=False,help="Display contents of .txt files")
parser.add_option("-p","--requirePlots",action="store_true",dest="requirePlots",default=False,help="Require plots to print directory")
parser.add_option("-d","--dirs",action="store_true",dest="dirs",default=False,help="Print directories")
parser.add_option("","--title",dest="title",type="string",default="",help="Set page title")
parser.add_option("","--description",dest="description",type="string",help="Add page description")
parser.add_option("","--width",dest="width",type="int",default=400,help="Set plot size")
parser.add_option("","--textHeight",dest="textHeight",type="int",default=400,help="Set expand text height")
parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="Print more output")
(options,args)=parser.parse_args()

directory = sys.argv[1]
types=['png','gif','txt','tex','pdf','jpg','C','root']
types.sort()
displayTypes=['png','gif','jpg','JPG']

def insertJavaDropDownScript(file):
  file.write('<script language=\"JavaScript\" type=\"text/javascript\">\n')
  file.write('if (document.getElementById) {\n')
  file.write('document.writeln(\'<style type=\"text/css\"><!--\')\n')
  file.write('document.writeln(\'.texter {display:none} @media print {.texter {display:block;}}\')\n')
  file.write('document.writeln(\'</style>\') }\n')
  file.write('function openClose(theID) {\n')
  file.write('if (document.getElementById(theID).style.display == \"block\") { document.getElementById(theID).style.display = \"none\" }\n')
  file.write('else { document.getElementById(theID).style.display = \"block\" } }\n')
  file.write('</script>\n')
  
# need to gather directory locations if displaying links
links=[]
if options.links:
  for root,dirs,files in os.walk(directory):
    if root.rsplit('/')==directory.rsplit('/'): continue
    plotsFound=False
    depth=root.rstrip('/').count('/')-directory.rstrip('/').count('/')
    for fType in types:
      if len(fnmatch.filter(files,"*.%s"%fType))>0: plotsFound=True
      else: continue
    if not options.requirePlots:
      links.append(root)
    else:
      if plotsFound:
        links.append(root)

# walk directories and make htmls
for root,dirs,files in os.walk(directory):
  # first check if this dir contains any relevant files (defined by types)
  sortedFiles=[]
  plotsFound=False
  for fType in types:
    if len(fnmatch.filter(files,"*.%s"%fType))>0: plotsFound=True
    else: continue
  if plotsFound:
    htmlFile = open(os.path.join(root,'default.html'),'w')
  # now loop the relevant files and put them in html list
  for fType in types:
    for filename in fnmatch.filter(files,"*.%s"%fType):
      #if filename=='default.html': continue
      pathToFile = os.path.join(root,filename)
      modTime = "%s" % time.ctime(os.path.getmtime(pathToFile))
      sortedFiles.append([filename,modTime,fType])
  
  if len(sortedFiles)==0: continue

  # sort files by date, type or name
  sortedFiles.sort(key=lambda x: x[0])
  if options.sortbytime:
    sortedFiles.sort(key=lambda x: x[1], reverse=True)
  if options.sortbytype:
    sortedFiles.sort(key=lambda x: x[2])

  # do some more sorting such that displayTypes come first
  if options.sortbytype:
    temp_sorted_files=[]
    for fType in displayTypes:
      temp_sorted_files += [el for el in sortedFiles if fType in el[2]]
    for fType in types:
      if fType in displayTypes: continue
      temp_sorted_files += [el for el in sortedFiles if fType in el[2]]
    sortedFiles=temp_sorted_files
 
  # print some not very helpful output
  if options.verbose:
    print os.path.basename(directory.rstrip('/'))
    print os.path.basename(root)
    print root
    print htmlFile.name
    print sortedFiles
    print '------------'

  # add title
  if options.title:
    if options.title=="": htmlFile.write('<font size=\"5\"> <u> Auto-generated from '+root+' </u> </font> <br>\n')
    else: htmlFile.write('<font size=\"5\"> <u> '+options.title+' </u> </font> <br>\n')
    htmlFile.write('<script language=\"Javascript\"> document.write(\"Last modified: \" + document.lastModified + \" (UTC)\"); </script> <br>\n')
    htmlFile.write('<br>\n')

  # add description
  if options.description:
    htmlFile.write('DESCRIPTION: <font size=\"4\"> '+options.description+' </font> <br><br> \n')

  # add notes
  if options.notes:
    htmlFile.write('<table>\n\t<tr>\n\t\t<td>NOTE: </td>\n\t\t<td>Plots will display as <b>.png</b>. The <b>.pdf</b> and <b>.jpg</b> versions, if available, can be obtained by clicking the relevant links.</td>\n\t</tr>\n\t<tr>\n\t\t<td></td>\n\t\t<td>Other formats, such as <b>.txt</b> and <b>.tex</b> files, are also accesible via links at the bottom.</td>\n\t</tr>\n\t<tr>\n\t\t<td></td>\n\t\t<td>Find other relevant plots by expanding <b>Other plots</b> (below) and following the links.</td>\n\t</tr>\n</table> <br> <br> \n')

  # add some fancy java to provide drop down lists
  insertJavaDropDownScript(htmlFile) 
  
  htmlFile.write('This directory: <font color=\"red\"><b> '+root.split(directory)[-1]+' </b></font> <br> <br>\n')
  # add links
  if options.links:
    htmlFile.write('<div onClick=\"openClose(\'links\')\" style=\"cursor:hand; cursor:pointer\"><b><u><font color=\"blue\"> Other plots: </font></u></b> (click to expand) </div> \n')
    htmlFile.write('<div id=\"links\" class=\"texter\"> \n')
    htmlFile.write('&#160; &#160; <a href=\"'+os.path.join(os.path.relpath(directory,root),os.path.basename(directory))+'\">parent</a> <br> \n')
    for link in links:
      depth=link.count('/')-directory.rstrip('/').count('/')
      tabs=" "
      for d in range(depth): tabs+='&#160; &#160; &#160; '
      htmlFile.write('&#160; '+tabs+'&#8627; <a href=\"'+os.path.relpath(link,root)+'\">'+os.path.basename(link)+'</a> <br> \n')
    htmlFile.write('</div>\n')
    htmlFile.write('<br>\n')
  
  # add contents
  if options.contents:
    htmlFile.write('<div onClick=\"openClose(\'contents\')\" style=\"cursor:hand; cursor:pointer\"><b><u><font color=\"blue\"> Contents: </font></u></b> (click to expand) </div> \n')
    htmlFile.write('<div id=\"contents\" class=\"texter\"> \n')
    for element in sortedFiles:
      filename=element[0]
      htmlFile.write('&#160; &#160; <a href=\"#'+filename+'\">'+filename+'</a> <br>\n')
    htmlFile.write('</div>\n')
    htmlFile.write('<br>\n')
 
  # add directories
  if options.dirs:
    htmlFile.write('<b>Folders:</b> <br> \n')
    htmlFile.write('&#160; &#160;')
    for dir in dirs:
      htmlFile.write('<a href=\"'+os.path.join(os.path.relpath(dir,root),os.path.basename(directory))+'\">'+dir+'</a>, &#160; \n')
    htmlFile.write('<br>\n')
  
  # write the html page
  htmlFile.write('<b>Images:</b> <br> \n')
  for element in sortedFiles:
    filename = element[0]
    pathToFile = os.path.join(root,filename)
    htmlFile.write('<a id=\"'+filename+'\" href='+filename+'>'+filename+'</a>')
    if filename.split('.')[-1] in displayTypes: htmlFile.write(' - Displayed below <br>\n')
    elif filename.split('.')[-1]=='txt' and options.expandText: htmlFile.write(' - Expanded below <br>\n')
    else: htmlFile.write(' - Click to download <br>\n')
    if options.sortbytime: htmlFile.write('Last Modified (%s)<br>\n' % time.ctime(os.path.getmtime(pathToFile)))
    if filename.split('.')[-1] in displayTypes: htmlFile.write('<a href='+filename+'><img height=\"'+str(options.width)+'\" src=\"'+filename+'\"></a><br>\n')
    if filename.split('.')[-1]=='txt' and options.expandText: htmlFile.write('<div id=\"list\"><p><iframe src=\"'+filename+'\" width=800 height='+str(options.textHeight)+'frameborder=0 ></iframe></p></div><br>\n')
