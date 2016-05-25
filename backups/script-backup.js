function getPage(url){
	console.log(url)
	$.ajax({
			url: 'proxy.php',
			type: 'POST',
			async: false,
			data: {
				address: url
			},
			success: function(data) {
						console.log("Succes");
						$("#content").html(data); 
						modifyContent(); //this function is called although the function above didn't finish
						console.log("OK2")
						}
		});
		setTimeout(modifyContent, 10000);
		//console.log("OK!");
};
function modifyContent(){
	$("#content").find("a")
				 .each(function(){
					$(this).removeAttr("href")});
	$("#content").children().toArray().forEach(function(e){console.log(e)});
				
	return $("#content");
};
function modifyLastChild(selector){
	//if (selector){
	//	var children = $(selector).children();
	//	console.log($(selector));
	//};
	//console.log($(selector))
	//console.log(children.length)
	//if(children && children.length){
	//	$.each(children, modifyLastChild(index, value));
	//}
	//else{
	//	$(selector).addClass("higlighted-blue");
	//}
};
$(document).ready(function(){
	$("#load_page").click(function(){
		getPage($("#page_url").val());
		//modifyContent();
		//setTimeout(modifyContent(), 10000);
			})
	$(document).keypress(function(e){
		if (e.which == 13) {
			getPage($("#page_url").val())
			//modifyContent()
			//setTimeout(modifyContent(), 10000);
			}
		})
});