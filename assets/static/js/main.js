$(function(){
	$(".carousel").carousel();
	$("#toTop").on("click",function(){
		$('body,html').animate({scrollTop:0},280);
	});
	function createDialogPage(content){
		var dialogPage = "<div id='dialogPage'>\
			<div class='container'>\
				<div class='row'>\
					<div class='dialog-background col-md-4 col-md-offset-4'>\
						<a id='closeDialogPage' href='javascript:void();' title='关闭登陆弹窗'><span class='glyphicon glyphicon-remove'></span>关闭</a>\
						" + content + "\
					</div>\
				</div>\
			</div>\
		</div>";
		// 添加弹窗
		$("body").append(dialogPage);
		// 点击关闭的事件
		$("#closeDialogPage").on("click",function(){
			// 移除弹窗页
			$('#dialogPage').remove();
			// 重置窗口大小事件
			window.onresize = windowOnresizeFunc;
		});
		// 更新弹窗页尺寸方法
		function updateDialogPageSize(){
			if ($('#dialogPage').length > 0) {
				$('#dialogPage').width(Math.max($(window).width(), $("body").width()));
				$('#dialogPage').height(Math.max($(window).height(), $("body").height()));
			}
		}
		updateDialogPageSize();
		// 监听窗口尺寸变化方法
		window.onresize = function(){
			if (windowOnresizeFunc != null) {
				windowOnresizeFunc();
			}
			updateDialogPageSize();
		}
	}
	var windowOnresizeFunc = window.onresize;
	$("#user").on("click",function(){
		var loginUrl = "http://jimdreamheart.club/pytoolsip/login";
		var createLoginDialog = function(){
			// 创建弹窗
			createDialogPage("<form class='login-form dialog-content' role='form'>\
							<h2>登陆PyToolsIP</h2>\
							<input id='loginUserName' class='form-control' type='text' placeholder='用户名' required autofocus />\
							<input id='loginPassword' class='form-control' type='password' placeholder='密码' required />\
							<label id='loginRemember'><input type='checkbox'> 记住密码</label>\
							<button id='loginButton' class='btn btn-lg btn-success btn-block' type='button'><span class='glyphicon glyphicon-log-in'></span>&nbsp;登陆</button>\
						</form>");
			// 绑定登陆按钮的点击事件
			$("#loginButton").on("click",function(){
				$.post(loginUrl, {
					name : $("#loginUserName").val(),
					password : $("#loginPassword").val(),
				}, function(data, status){
					if (status == "success" && data.isSuccess) {
						console.log("登陆成功。");
						$.cookie("uid", data.uid, {expires: 1, path: "/pytoolsip", domain: "http://jimdreamheart.club"});
						if ($('#dialogPage').length > 0) 	{
							$('#dialogPage').remove();
						}
					} else {
						alert("登陆失败！")
					}
				});
			});
		}
		var $uid = $.cookie("uid");
		if ($uid == undefined) {
			createLoginDialog();
		} else {
			$.post(loginUrl, {
				uid : $uid,
			}, function(data, status){
				console.log("data", data)
				if (status == "success" && data.isSuccess) {
					createDialogPage("\
								<div class='dialog-content'>\
									<h2>玩家信息</h2>\
									<p>用户名：<span>" + data.name + "</span></p>\
									<p>邮箱：<span>" + data.email + "</span></p>\
								</div>");
				} else {
					createLoginDialog();
				}
			});
		}
	});
})