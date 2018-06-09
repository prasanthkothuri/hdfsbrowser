// file js/HdfsBrowser.js

define([
    'base/js/namespace'
], function(
    Jupyter
) {
    function load_ipython_extension() {

        var handler = function () {
             // alert('this is an alert from my_extension!');
                console.log("hdfsbrowser: ", Jupyter.notebook.base_url)
    		var iframe = $('\
                    <div style="overflow:scroll">\
                    <iframe src="'+ Jupyter.notebook.base_url + 'hdfsbrowser/explorer.html' + '" frameborder="0" scrolling="yes" class=hdfsbrowserframe>\
                    </iframe>\
                    </div>\
                    ');
                iframe.find('.hdfsbrowserframe').width('100%');
	        iframe.find('.hdfsbrowserframe').height('100%');
    		iframe.dialog({
        		title: "HDFS Browser",
        		width: 1000,
        		height: 500,
        		autoResize: true,
        		dialogClass: "hdfs-browser-dialog"
    			});

        };

        var action = {
            icon: 'fa-folder-open', // a font-awesome class used on buttons, etc
            help    : 'hdfs browser',
            help_index : 'zz',
            handler : handler
        };

        var prefix = 'hdfs_browser';
        var action_name = 'open-iframe';

        var full_action_name = Jupyter.actions.register(action, action_name, prefix); // returns 'hdfs_browser:open-iframe'
        Jupyter.toolbar.add_buttons_group([full_action_name]);
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
