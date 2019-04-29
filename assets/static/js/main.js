$(function(){
	$('.carousel').carousel();
	$("#toTop").on("click",function(){
		$('body,html').animate({scrollTop:0},280);
	});
})