Jupyter notebook extension to browse HDFS filesystem, works with kerberos and basic authentication

#### Install client extension

sudo jupyter nbextension install hdfsbrowser/extension/js/

#### Enable client extension

sudo jupyter nbextension enable js/HdfsBrowser

#### Install server extension

sudo pip install hdfsbrowser/extension/

#### To load (use) server extension
export HDFS_NAMENODE_HOST=_namenode_
jupyter notebook --NotebookApp.nbserver_extensions="{'hdfsbrowser.serverextension':True}" --allow-root --ip=xx.xx.xx.xx
