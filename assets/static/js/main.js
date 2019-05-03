$(function(){
	$(".carousel").carousel();
	$("#toTop").on("click",function(){
		$('body,html').animate({scrollTop:0},280);
	});
	// 响应窗口尺寸大小变化函数
	var windowOnresizeFunc = window.onresize;
	// 登陆链接
	var loginUrl = "http://jimdreamheart.club/pytoolsip/login";
	// 创建弹窗函数
	function createDialogPage(content){
		var dialogPage = "<div id='dialogPage'>\
			<div class='container'>\
				<div class='row'>\
					<div class='dialog-background col-md-4 col-md-offset-4'>\
						<a id='closeDialogPage' href='javascript:void(0);' title='关闭登陆弹窗'><span class='glyphicon glyphicon-remove'></span>关闭</a>\
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
	function createLoginDialog(){
		// 创建弹窗
		createDialogPage("<form class='login-form dialog-content' role='form'>\
						<h2>登陆PyToolsIP</h2>\
						<input id='loginUserName' class='form-control' type='text' placeholder='用户名' required autofocus />\
						<input id='loginPassword' class='form-control' type='password' placeholder='密码' required />\
						<label id='loginRemember'><input type='checkbox'>&nbsp;记住用户</label>\
						<button id='loginButton' class='btn btn-lg btn-success btn-block' type='button'><span class='glyphicon glyphicon-log-in'></span>&nbsp;登陆</button>\
						<label>注：本平台暂不支持网页注册。如需注册，请通过<a href='http://jimdreamheart.club/pytoolsip'>首页</a>下载并运行PyToolsIP，选择【用户>注册】进行注册。</label>\
					</form>");
		// 绑定登陆按钮的点击事件
		$("#loginButton").on("click",function(){
			$.session.set("isRememberMe", $("#loginRemember>input[type='checkbox']").is(":checked"));
			console.log("isRememberMe:", $.session.get("isRememberMe"))
			$.post(loginUrl, {
				name : $("#loginUserName").val(),
				password : $("#loginPassword").val(),
			}, function(data, status){
				if (status == "success" && data.isSuccess) {
					console.log("登陆成功。");
					if ($.session.get("isRememberMe") == true) {
						$.cookie("uid", data.uid, {expires: 1, path: "/"});
					} else {
						$.session.set("uid", data.uid);
						console.log("session uid:", $.session.get("uid"));
					}
					if ($('#dialogPage').length > 0) 	{
						$('#dialogPage').remove();
					}
				} else {
					alert("登陆失败！")
				}
			});
		});
	}
	function createLogoutDialog(data){
		// 创建弹窗
		createDialogPage("<div class='dialog-content text-center'>\
							<h2>玩家信息</h2>\
							<p>用户名：<span>" + data.name + "</span></p>\
							<p>邮箱：<span>" + data.email + "</span></p>\
							<button id='logoutButton' class='btn btn-default btn-block' type='button' style='margin-top:30px;'><span class='glyphicon glyphicon-log-out'></span>&nbsp;注销账号</button>\
						</div>");
		// 绑定注销按钮的点击事件
		$("#logoutButton").on("click",function(){
			$.cookie("uid", null, {expires: 1, path: "/"});
			$.session.remove("uid");
			if ($('#dialogPage').length > 0) 	{
				$('#dialogPage').remove();
			}
			// 创建登陆弹窗
			createLoginDialog();
		});
	}
	// 获取玩家ID
	function getUid() {
		var $uid = $.cookie("uid");
		if ($uid == undefined || $uid == "null") {
			$uid = $.session.get("uid");
		}
		if ($uid == undefined || $uid == "null") {
			return null;
		}
		return $uid;
	}
	// 点击用户事件
	$("#user").on("click",function(){
		var $uid = getUid();
		if ($uid == undefined) {
			createLoginDialog();
		} else {
			$.post(loginUrl, {
				uid : $uid,
			}, function(data, status){
				console.log("data", data)
				if (status == "success" && data.isSuccess) {
					createLogoutDialog(data);
				} else {
					createLoginDialog();
				}
			});
		}
	});
	// 评论按钮点击事件
	$("#commentButton").click(function(){
		var $uid = getUid();
		if ($uid == undefined) {
			createLoginDialog();
			return;
		}
		var $content = $("#commentContent").val();
		if ($content == "") {
			alert("评论内容不能为空！");
			return;
		}
		$.post("http://jimdreamheart.club/pytoolsip/detail?t={{ toolInfo.tkey }}",{
			uid : $uid,
			content : $content,
			score : $("#commentScore").val(),
		}, function(data,status){
			if (status != "success") {
				alert("提交评论失败，请重新提交！")
			}
		});
	});
})