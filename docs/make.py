import os
from git import Repo
from time import strftime, localtime

os.system(".\\make.bat clean")
oRepo = Repo("..\\")
gComTag = oRepo.head.commit.hexsha[:7]
gDirty = "*" if oRepo.is_dirty else ""
gComTime = strftime("%a, %d %b %Y, %H:%M:%S", localtime(oRepo.head.commit.committed_date))
f = open('build\\copyright', 'wt')
f.write('2023, Jonathan Marks, Commit Tag: ' + gComTag + gDirty + ', ' + gComTime)
f.close()
os.system(".\\make.bat html")