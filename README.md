Install client extension

sudo jupyter nbextension install hdfsbrowser/extension/js/

Enable client extension

sudo jupyter nbextension enable js/HdfsBrowser

Install server extension

sudo pip install hdfsbrowser/extension/

To load (use) server extension

jupyter notebook --NotebookApp.nbserver_extensions="{'hdfsbrowser.serverextension':True}" --allow-root --ip=xx.xx.xx.xx
