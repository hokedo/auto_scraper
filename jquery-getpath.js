/*
	jQuery-GetPath v0.01, by Dave Cardwell. (2007-04-27)
	
	http://davecardwell.co.uk/javascript/jquery/plugins/jquery-getpath/
	
	Copyright (c)2007 Dave Cardwell. All rights reserved.
	Released under the MIT License.
	
	
	Usage:
	var path = $('#foo').getPath();
*/

jQuery.fn.extend({
	getPath: function( path, count , type) {
		// 
		// The first time this function is called, path won't be defined.
		if ( typeof path == 'undefined' ) {
			path = '';
			count = 0;
		}
		//console.log(type)
		if (type == "review"){
			if ( count == 2){
				return SlicePath(path);
				}
		else{
			if ( count == 5){
				return SlicePath(path);
				}
			}
		}
		// If this element is <div id="content" class="modified"> we've reached the end of the path.
		if ( this.is('div#content.modified') ){
				return SlicePath(path);
		}

		// Add the element name.
		var cur = this.get(0).nodeName.toLowerCase();

		// Determine the IDs and path.
		var id    = this.attr('id')
		var	clss  = this.attr('class');


		// Add the #id if there is one.
		if ( typeof id != 'undefined' )
			cur += '#' + id;

		// Add any classes.
		if ( typeof clss != 'undefined' )
			cur += '.' + clss.split(/[\s\n]+/).join('.');

		// Recurse up the DOM.
		return this.parent().getPath( ' > ' + cur + path , count+1, type);
	}
});

function SlicePath(path){
	if ( path[path.length - 1] == '.' ) 
	{
		path = path.slice(0, path.length-1);
	};
	if ( path[1] == '>' ){
		path = path.slice(3, path.length);
	}
	return path;
}