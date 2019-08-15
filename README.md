# arxiv-cleaner
Simple tool to clean your TeX project before ArXiv upload

## Motivation 
When you want to upload your paper to [ArXiv](https://arxiv.org), it requires you to provide
a source code for your paper (to insert a watermark, actually). But after that, they make
your sources publicly available. Sometimes you (like me) have a commented text or stale figures
remaining from other submissions, so you not not want to share all of that. To help with this 
issue I wrote this tool. It also could be useful to clean your TeX project before uploading it
to a conference site. Enjoy.

## Usage
The tool could be used in two modes. The first one if you have a project folder somewhere. 
Then you simply run it with a path to main file your project:

```bash
python clean.py  path/to/project/main.tex
```

The second option, if you have a zip file containing your project folder (for example, 
downloaded) from [overleaf.com](https://overleaf.com). Then you need in addition to a path to the zip file, 
also provide the tool with main file name, like that:

```bash
python clean.py -m main.tex path/to/project.zip
```

## Acknowledgments
I would like to thank my colleagues from Saint-Petersburg Department of Steklov Mathematical 
Institute for their patience in this simple task of uploading a paper to ArXiv. 