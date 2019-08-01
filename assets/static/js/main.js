$(function(){
	$(".carousel").carousel();
	$("#toTop").on("click",function(){
		$('body,html').animate({scrollTop:0},280);
	});
	// 响应窗口尺寸大小变化函数
	var windowOnresizeFunc = window.onresize;
	// 登陆链接
	var loginUrl = "http://localhost:8000/login";
	// 注册链接
	var registerUrl = "http://jimdreamheart.club/pytoolsip/register";
	// 获取提示文档
	var getAlertTips = function(type, tips) {
		return "<div class='alert alert-"+ type +"' role='alert'>\
			<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\
			<span class='alertContent'>"+ tips +"</span>\
		</div>";
	}
    // 设置玩家登录信息
    setUserLoginInfo = function(name, pwd, expires){
        $.cookie("ptip_username", name, {expires: expires, path: "/"});
        $.cookie("ptip_userpwd", pwd, {expires: expires, path: "/"});
    }
    // 获取玩家登录信息
    getUserLoginInfo = function(){
        var $uname = $.cookie("ptip_username");
        var $upwd = $.cookie("ptip_userpwd");
        if ($uname == undefined || $uname == "null") {
            $uname = "";
        }
        if ($upwd == undefined || $upwd == "null") {
            $upwd = "";
        }
        return {
            "name" : $uname,
            "pwd" : $upwd,
        };
	}
	// 登陆平台
    loginIP = function(url, formId, isRemember, callback){
		var name = $("#"+formId+" input[name='name']").val();
		var pwd = $("#"+formId+" input[name='password']").val();
		console.log("===== loginIP =====", formId, name, pwd);
        $.post(url, {
			isReqLogin : true,
			uname : name,
		}, function(data, status){
			if (status == "success") {
				if (!data.isSuccess) {
					$("#"+formId).prepend(getAlertTips("danger", data.tips));
					return;
				}
				// 提交登陆数据
				$.post(url, {
                    isLogin : true,
                    uname : name,
                    upwd : eval(data.encodePwd.replace(/\$1/, pwd)),
					isRemember : isRemember,
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#"+formId).prepend(getAlertTips("danger", data.tips));
							return;
						}
						console.log("登陆成功。");
						// 缓存登陆数据
						setUserLoginInfo(data.name, data.pwd, data.expires);
						// 登陆成功回调
						callback();
					} else {
						alert("登陆失败！")
					}
				});
			} else {
				alert("请求登陆失败！")
			}
		});
    }
	// 关闭弹窗
	var closeDialogPage = function(){
		if ($('#dialogPage').length > 0) 	{
			$('#dialogPage').remove();
		}
	}
	// 创建弹窗函数[带有关闭回调参数]
	function createDialog(content, closeCallback){
		// 关闭原有弹窗
		closeDialogPage();
		// 弹窗内容
		var dialogPage = "<div id='dialogPage'>\
			<div class='container'>\
				<div class='row'>\
					<div class='dialog-background col-md-4 col-md-offset-4'>\
						<a id='closeDialogPage' href='javascript:void(0);' title='关闭弹窗'><span class='glyphicon glyphicon-remove'></span>关闭</a>\
						<div class='dialog-content'>" + content + "</div>\
					</div>\
				</div>\
			</div>\
		</div>";
		// 添加弹窗
		$("body").append(dialogPage);
		// 点击关闭的事件
		$("#closeDialogPage").on("click",function(){
			// 移除弹窗页
			closeDialogPage();
			// 重置窗口大小事件
			window.onresize = windowOnresizeFunc;
			// 回调关闭函数
			closeCallback();
		});
		// 更新弹窗页尺寸方法
		function updateDialogPageSize(){
			if ($('#dialogPage').length > 0) {
				var pageWidth = Math.max($(window).width(), $("body").width());
				$('#dialogPage').width(pageWidth);
				var pageHeight = Math.max($(window).height(), $("body").height());
				$('#dialogPage').height(pageHeight);
				// 移动到弹窗中心
				$('body,html').animate({scrollLeft : (pageWidth - $(window).width())/2, scrollTop: (pageHeight - $(window).height())/2},280);
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
	// 创建弹窗函数
	function createDialogPage(content){
		createDialog(content, function(){}); // 关闭弹窗时无回调
	}
	// 创建定时弹窗
	function createIntervalDialog(content, seconds){
		// 设置定时器
		var intervalId = window.setInterval(function(){
			seconds--
			if (seconds < 0) {
				window.clearInterval(intervalId);
				//关闭弹窗
				closeDialogPage();
			}
			if ($('#timeCountDown').length > 0) {
				$('#timeCountDown').html(seconds);
			}
		}, 1000);
		// 创建弹窗
		createDialog("<div class='text-center'>"+ content +"<p class='dialog-interval'><span id='timeCountDown'>"+ seconds +"</span>&nbsp;秒后自动关闭</p></div>", function(){
			window.clearInterval(intervalId);
		});
	}
	// 创建登录弹窗
	function createLoginDialog(){
		// 创建弹窗
		createDialogPage("<form id='loginForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>登陆PyToolsIP</h2>\
						<input name='name' class='form-control' type='text' placeholder='用户名' required autofocus />\
						<input name='password' class='form-control' type='password' placeholder='密码' required />\
						<label id='loginRemember'><input type='checkbox'>&nbsp;记住用户</label>\
						<button class='btn btn-lg btn-success btn-block' type='submit'><span class='glyphicon glyphicon-log-in'></span>&nbsp;登陆</button>\
						<div class='login-link clearfix'>\
							<a id='registerDialog' class='pull-left' href='javascript:void(0)'>注册用户</a>\
							<a id='forgetDialog' class='pull-right' href='javascript:void(0)'>重置密码</a>\
						</div>\
					</form>");
		// 登陆校验
		$("#loginForm").validate({
			rules: {
				name: {
					required: true,
				},
				password: {
					required: true,
				},
			},
			messages: {
				name: {
					required: "请输入用户名",
				},
				password: {
					required: "请输入密码",
				},
			},
			submitHandler: function() {
				loginIP(loginUrl, "loginForm", $("#loginRemember>input[type='checkbox']").is(":checked"), function(){
					// 关闭弹窗
					closeDialogPage();
				});
			}
		});
		// 绑定注册超链接的点击事件
		$("#registerDialog").on("click",function(){
			createRegisterDialog();
		});
		// 绑定更新密码超链接的点击事件
		$("#forgetDialog").on("click",function(){
			createForgetDialog();
		});
	}
	// 创建登出弹窗
	function createLogoutDialog(data){
		// 创建弹窗
		createDialogPage("<div class='text-center'>\
							<h2>玩家信息</h2>\
							<p>用户名：<span>" + data.name + "</span></p>\
							<p>邮箱：<span>" + data.email + "</span></p>\
							<button id='logoutButton' class='btn btn-default btn-block' type='button' style='margin-top:30px;'><span class='glyphicon glyphicon-log-out'></span>&nbsp;退出账号</button>\
						</div>");
		// 绑定注销按钮的点击事件
		$("#logoutButton").on("click",function(){
			// 重置玩家的登录信息
			setUserLoginInfo(null, null, 0);
			// 关闭弹窗
			closeDialogPage();
			// 创建登陆弹窗
			createLoginDialog();
		});
	}
	// 点击用户事件
	$("#user").on("click",function(){
		var userInfo = getUserLoginInfo();
		if (userInfo.name == "" || userInfo.pwd == "") {
			createLoginDialog();
		} else {
			$.post(loginUrl, {
				uname : userInfo.name,
				upwd : userInfo.pwd,
			}, function(data, status){
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
		var userInfo = getUserLoginInfo();
		if (userInfo.name == "" || userInfo.pwd == "") {
			createLoginDialog();
			return;
		}
		var $content = $("#commentContent").val();
		if ($content == "") {
			alert("评论内容不能为空！");
			return;
		}
		$.post("http://jimdreamheart.club/pytoolsip/detail?t={{ toolInfo.tkey }}",{
			uname : userInfo.name,
			upwd : userInfo.pwd,
			content : $content,
			score : $("#commentScore").val(),
		}, function(data,status){
			if (status != "success") {
				alert("提交评论失败，请重新提交！")
			}
		});
	});
	// 创建注册弹窗
	function createRegisterDialog(){
		// 创建弹窗
		createDialogPage("<form id='registerForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>PyToolsIP用户注册</h2>\
						<input name='name' class='form-control' type='text' placeholder='用户名' required autofocus />\
						<input id='password' name='password' class='form-control' type='password' placeholder='密码' required />\
						<input id='verifyPwd' name='verifyPwd' class='form-control' type='password' placeholder='确认密码' required />\
						<input name='email' class='form-control' type='text' placeholder='邮箱' required />\
						<div class='input-group'>\
							<input name='verifyCode' class='form-control' type='text' placeholder='验证码' required />\
							<span class='input-group-btn'>\
								<button id='verifyCodeBtn' class='btn btn-default' type='button'>获取验证码</button>\
							</span>\
						</div>\
						<button class='btn btn-lg btn-success btn-block' type='submit'><span class='glyphicon glyphicon-registration-mark'></span>&nbsp;注册</button>\
					</form>");
		// 绑定登陆按钮的点击事件
		$("#registerForm").validate({
            rules: {
                name: {
                    required: true,
                    rangelength: [2, 10],
                },
                password: {
                    required: true,
                    rangelength: [6, 16],
                },
                verifyPwd: {
                    required: true,
                    rangelength: [6, 16],
                    equalTo: "#password"
                },
                email: {
                    required: true,
                    email: true
                },
                verifyCode: {
                	required: true,
                }
            },
            messages: {
                name: {
                    required: "请输入用户名",
                    rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
                },
                password: {
                    required: "请输入密码",
                    rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
                },
                verifyPwd: {
                    required: "请输入确认密码",
                    rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
                    equalTo: "确认密码和密码不匹配"
                },
                email: {
                    required: "请输入邮箱",
                    email: "邮箱格式有误",
                },
                verifyCode: {
                	required: "请输入验证码",
                }
            },
            submitHandler: function() {
                $.post(registerUrl, {
					uname : $("#registerForm input[name='name']").val(),
					upwd : $("#registerForm input[name='password']").val(),
					email : $("#registerForm input[name='email']").val(),
					verifyCode : $("#registerForm input[name='verifyCode']").val(),
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#registerForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						// 创建登录成功的弹窗
						createIntervalDialog("<h2>注册成功!</h2>", 2);
					} else {
						alert("注册失败！")
					}
				});
            }
       });
	}
	// 创建更新密码弹窗
	function createForgetDialog(){
		// 创建弹窗
		createDialogPage("<form id='forgetForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>PyToolsIP更新密码</h2>\
						<input id='password' name='password' class='form-control' type='password' placeholder='新密码' required />\
						<input id='verifyPwd' name='verifyPwd' class='form-control' type='password' placeholder='确认密码' required />\
						<input name='email' class='form-control' type='text' placeholder='注册邮箱' required />\
						<div class='input-group'>\
							<input name='verifyCode' class='form-control' type='text' placeholder='验证码' required />\
							<span class='input-group-btn'>\
								<button id='verifyCodeBtn' class='btn btn-default' type='button'>获取验证码</button>\
							</span>\
						</div>\
						<button class='btn btn-lg btn-success btn-block' type='submit'><span class='glyphicon glyphicon-registration-mark'></span>&nbsp;更新密码</button>\
					</form>");
		// 绑定登陆按钮的点击事件
		$("#forgetForm").validate({
            rules: {
                password: {
                    required: true,
                    rangelength: [6, 16],
                },
                verifyPwd: {
                    required: true,
                    rangelength: [6, 16],
                    equalTo: "#password"
                },
                email: {
                    required: true,
                    email: true
                },
                verifyCode: {
                	required: true,
                }
            },
            messages: {
                password: {
                    required: "请输入密码",
                    rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
                },
                verifyPwd: {
                    required: "请输入确认密码",
                    rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
                    equalTo: "确认密码和密码不匹配"
                },
                email: {
                    required: "请输入邮箱",
                    email: "邮箱格式有误",
                },
                verifyCode: {
                	required: "请输入验证码",
                }
            },
            submitHandler: function() {
                $.post(registerUrl, {
					upwd : $("#registerForm input[name='password']").val(),
					email : $("#registerForm input[name='email']").val(),
					verifyCode : $("#registerForm input[name='verifyCode']").val(),
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#forgetForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						// 创建登录成功的弹窗
						createIntervalDialog("<h2>密码更新成功!</h2>", 2);
					} else {
						alert("注册失败！")
					}
				});
            }
       });
	}
	
//	// 定时弹窗
//	if ($('.jumbotron').length > 0) {
//		createIntervalDialog("<h2>定时弹窗</h2><p>测试...</p>", 5);
//	}
})