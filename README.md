# DelayNoMore

To deal with GitHub's limited storage, we have provisioned a temporary solution for our data storage.

For every notebook analysis you would do, please separate it out into your own folder.

Every folder must contain a "data" folder within it, this is where your data would come from.

Within said "data" folder must contain a .gitignore with the contents of :
*
!.gitignore

Once the .gitignore has been added, you need to force add it to git by running 'git add -f .gitignore' in the "data" folder.

You can then run 'python3 s3Upload.py' and follow the instructions there.

"data" folders will not be downloaded by default, to download an analysis' data folder, run 'python3 s3Download.py' and follow the instructions there.