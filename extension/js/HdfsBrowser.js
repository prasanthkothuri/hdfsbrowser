// file js/HdfsBrowser.js

define([
    'base/js/namespace',
    'base/js/events',
    'require'
], function(
    Jupyter, events, requirejs
) {
    function load_ipython_extension() {

        // add css
        $('<link rel="stylesheet" type="text/css">')
           .attr('href', requirejs.toUrl('./icon.css'))
           .appendTo('head');

        var handler = function () {
                // console.log("hdfsbrowser: ", Jupyter.notebook.base_url)
    		var iframe = $('\
                    <div style="overflow:hidden">\
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
            // icon: 'fa-folder-open', // a font-awesome class used on buttons, etc
            icon: 'fa-fw', // a font-awesome class used on buttons, etc
            help    : 'hdfs browser',
            help_index : 'zz',
            handler : handler
        };

        var prefix = 'hdfs_browser';
        var action_name = 'open-iframe';

        var full_action_name = Jupyter.actions.register(action, action_name, prefix); // returns 'hdfs_browser:open-iframe'
        // Jupyter.toolbar.add_buttons_group([full_action_name]);
        this.toolbar_button = Jupyter.toolbar.add_buttons_group([full_action_name]).find('.btn');
        this.toolbar_button.addClass('hadoop-icon');

        // Jupyter.notebook.events.on('kernel_ready.Kernel', function() {
        // this.toolbar_button.addClass('active');
        //  });

    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
