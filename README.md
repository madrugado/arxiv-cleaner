# arxiv-cleaner
Simple tool to clean your TeX project before ArXiv upload

## Motivation 
When you want to upload your paper to [ArXiv](https://arxiv.org), it requires you to provide
a source code for your paper (to insert a watermark, actually). But after that, they make
your sources publicly available. Sometimes you (like me) have a commented text or stale figures
remaining from the other submissions, and you do not like to share all of that. To help with this 
issue I wrote this tool. It also could be useful to clean your TeX project before uploading it
to a conference site. Enjoy.

## Usage
This tool is written in Python 3 <sub><sup>(with all my love to Python 2, it is outdated, Good night, sweet prince!)</sup></sub>. 
The tool could be used in two modes. The first one if you have a project folder somewhere. 
Then you simply run it with a path to main file your project:

```bash
python3 clean.py path/to/project/main.tex
```

The second option, if you have a zip file containing your project folder (for example, 
downloaded from [overleaf.com](https://overleaf.com)). Then you need in addition to a path to the zip file, 
also provide the tool with a main file name, like that:

```bash
python3 clean.py -m main.tex path/to/project.zip
```

## Acknowledgments
I would like to thank my colleagues from Saint-Petersburg Department of Steklov Mathematical 
Institute for their patience in this simple task of uploading a paper to ArXiv. 