var server_address = "127.0.0.1:8080";
var classifications = {};
var selectors = {};
var color_codes = {
	"title": "highlighted-green",
	"address": "hotel_address",
	"type": "highlighted-gray",
	"REVIEW_TITLE": "highlighted-black",
	"REVIEW_AUTHOR": "review_red",
	"REVIEW_DATE": "review_date",
	"price": "highlighted-orange"
};
function requestPage(url){
	console.log("Creating request to python server for the page html")
	objects = {"page_url" : url};
	$.getJSON('http://' + server_address + '/?callback=?',
			objects, 
			function(data){
						console.log("Succes");
						try{
							selectors = data["selectors"];
							console.log(selectors)
							$("#content").html(data["html"])
										 .removeClass("not-modified")
				 						 .addClass("modified");
							//document.getElementById("content").innerHTML = data["html"];
						}catch(e){
							console.log("requestPage() -> Setting up #content html ERROR");
						}
						//modifyContent(); 
						selectClickableEvent()
						highlightText();
						fillInputFields();
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
	object.selector = object.selector.replace(".SpecialClickable", "").replace(".highlighted-blue", "")
	$.getJSON('http://' + server_address + '/?callback=?',
				  		   object,
				  		   function(data){
				  		   		if(data.type in classifications){
				  		   			if(!classifications[data.type].includes(object.selector)){
				  		   				classifications[data.type].push(object.selector)
				  		   			};
				  		   		}
				  		   		else{
				  		   			classifications[data.type] = [object.selector];
				  		   		}
				  		   		filter_classifications();
				  		   	}
				  		   );
	}

function fillInputFields(){
	Object.keys(selectors).forEach(function(element, index, array){
		selector = "input[name='" + element + "']";
		input_field = $(selector);
		if(input_field.length > 0){
			input_field.attr("value", selectors[element]);
		}
	})
};

function highlightText(){
	Object.keys(selectors).forEach(function(item, index, array){
		if(item in color_codes){
			$(selectors[item]).addClass(color_codes[item]);
		}
	})
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

function filter_classifications(){
	//filter title selectors
	if(typeof(classifications["HOTEL_NAME"]) != 'undefined' && 'forEach' in classifications["HOTEL_NAME"]){
		classifications["HOTEL_NAME"].forEach(function(element, index, array){
			if($(element).length == 1 && !ContainsOthers(element, array)){
				if(typeof(selectors["HOTEL_NAME"]) != 'undefined'){
					if(!selectors["HOTEL_NAME"].includes(element)){
						selectors["HOTEL_NAME"].push(element)
					}
					for(var i = 0; i < selectors["HOTEL_NAME"].length; i++){
						if($(selectors["HOTEL_NAME"][i]).length > 1 && !ContainsOthers(selectors["HOTEL_NAME"][i], array)){
							selectors["HOTEL_NAME"].splice(i, 1);
						};
					};
				}
				else{
					selectors["HOTEL_NAME"] = [element];
				}
				var random_item = RandomArrayElement(classifications["HOTEL_NAME"]);
				$("*").removeClass(color_codes["HOTEL_NAME"])
				$(random_item).addClass(color_codes["HOTEL_NAME"]);
			}
		})
	}
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

function RandomArrayElement(array){
	return array[Math.floor(Math.random()*array.length)]
};

function ContainsOthers(item, array){
	for(var i = 0; i < array.length; i++){
		if(item != array[i] && $(item).text().indexOf($(array[i]).text()) > -1){
			return true;
		}
	}
	return false;
};

function selectClickableEvent(){
	$(".SpecialClickable").click(function(e){ 
			//Get the path of the clicked element and put in the input box and
			//highlight the element yellow to check if the selection is correct
			if($("input.Selected").attr("class").search("hotel_item") > -1 ){
				var path = $(e.target).removeClass("highlighted-blue SpecialClickable")
										.getPath(undefined, 0, "hotel");
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