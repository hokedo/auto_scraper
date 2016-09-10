var server_address = "127.0.0.1:8080";
var classifications = {};
var color_codes = {
	"HOTEL_NAME": "highlighted-green",
	"REVIEW_TEXT": "orange"
};
function requestPage(url){
	console.log("Creating request to python server for the page html")
	objects = {"page_url" : url};
	$.getJSON('http://' + server_address + '/?callback=?',
			objects, 
			function(data){
						console.log("Succes");
						try{
							$("#content").html(data["html"]);
							//document.getElementById("content").innerHTML = data["html"];
						}catch(e){
							console.log("requestPage() -> Setting up #content html ERROR");
						}
						modifyContent(); 
						selectClickableEvent()
				});
	}

function generate_scripts(objects){
	console.log("Creating request to python server to create the data extractor")
	$.getJSON('http://' + server_address + '/?callback=?',
			objects, 
			function(data){
						console.log(data);
						download_file("data_extractor_test.py", "http://localhost:8080/static/test.py")
				});
};

function classify_text_request(object){
	//object = {'selector' : <selector>, 'text': <text>}
	console.log("Creating request to python server")
	$.getJSON('http://' + server_address + '/?callback=?',
				  		   object,
				  		   function(data){
				  		   		classifications[object.selector] = data.type;
				  		   		if(data.type in color_codes){
				  		   			$(object.selector).attr("class", color_codes[data.type]);
				  		   		}
				  		   	}
				  		   );
	
	}

function modifyContent(){
	$("#content").find("a")
				 .each(function(){
					$(this).removeAttr("href")});
	$('#content').children()
				 .toArray()
				 .forEach(makeClickable);
	$("#content").removeClass("not-modified")
				 .addClass("modified");
	$("#content").children()
				 .toArray()
				 .forEach(classify);
				 //leave it here for the moment
				 //probably it modifies something in the dom
				 //and the other modification don't apply anymore
};

function classify(element, index, array){
	var elem = $(element)
	var text = validate(elem);

	if(text){
		classify_text_request({
			'selector': elem.getPath(),
			'text': text
		})
		
	}
	if(elem.children().length > 0){
		elem.children().toArray().forEach(classify)
	}
};

function makeClickable(element, index, array){
	//highlight the selectable text in blue if you hover over it
	var elem = $(element)
	if(validate(elem)){
		elem.addClass("highlighted-blue SpecialClickable");
	}
	if(elem.children().length > 0){
		elem.children().toArray().forEach(makeClickable)
	}
};

var validate = function(elem) { 
	//check if the element contains text without taking the children into account
	var element = elem.clone();
	element = $(element).children().remove().end().text($.trim($(element).text()));
	if(element.text().trim().length > 0)
		{	
			return element.text().trim();
		}
	else {
		return false;
	}
};

function FindReviewFrame(text_path){
	var total_reviews = $(text_path).length;
	var current_item = text_path;
	while (true){
		if($($(current_item).parent().getPath()).length == total_reviews){
			current_item = $(current_item).parent().getPath();
		}else {
			break;
		}
	}
	return current_item
};

function download_file(name, path){
	//name = file.extension
	//path = http://localhost:8081/file.extension
	
	/////////////////
	var milliseconds = 1000;
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds){
	 	 break;
		}
  	}
	////////////////

	var link = document.createElement('a');
	link.download = name
	link.href = path;

	// Because firefox not executing the .click() well
	// We need to create mouse event initialization.
	var clickEvent = document.createEvent("MouseEvent");
	clickEvent.initEvent("click", true, true);

	link.dispatchEvent(clickEvent);
}


function selectClickableEvent(){
	$(".SpecialClickable").click(function(e){ 
			//Get the path of the clicked element and put in the input box and
			//highlight the element yellow to check if the selection is correct
			if($("input.Selected").attr("class").search("hotel_item") > -1 ){
				var path = $(e.target).removeClass("highlighted-blue SpecialClickable")
										.getPath();
			}else {
				var path = $(e.target).removeClass("highlighted-blue SpecialClickable")
										.getPath(undefined, undefined, "review");
			}
			$("input.Selected").val(path).removeClass("Selected")
			$("input#ToSelect").toArray()
								 .forEach(function(e){
										path = $(e).val();
										$(path).addClass("highlighted-yellow");
								 });
			console.log(FindReviewFrame($("input#ToSelect[name='text']").val()));
			});
}

//MAIN
$(document).ready(function(){
	$("#load_page").click(function(){
		requestPage($("#page_url").val());
		});
	$("input#ToSelect").click(function(e){
		$(e.target).addClass("Selected");
	});
	$(document).keypress(function(e){
		if (e.which == 13) {
			getPage($("#page_url").val());
			}
		});
	$("#generate_scripts").click(function(){
		var hotel_items = {}
		var review_items = {}
		$(".hotel_item").toArray().forEach(function(item){
												hotel_items[$(item).attr("name")] = $(item).val();
												});
		$(".review_item").toArray().forEach(function(item){
												review_items[$(item).attr("name")] = $(item).val();
												});
		var review_frame = FindReviewFrame($("input#ToSelect[name='text']").val());
		var objects = {"hotel_items":hotel_items,
						"review_items":review_items,
						"review_frame":review_frame}
		generate_scripts(objects);
		//download_file("data_extractor_test.py", "http://localhost:8081/test.py")							  
	});
	
});