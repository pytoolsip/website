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
	createDialog = function(content, closeCallback){
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
	createDialogPage = function(content){
		createDialog(content, function(){}); // 关闭弹窗时无回调
	}
	// 创建定时弹窗
	createIntervalDialog = function(content, seconds){
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
	createLoginDialog = function(){
		// 创建弹窗
		createDialogPage("<form id='loginForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>登陆PyToolsIP</h2>\
						<input name='name' class='form-control' type='text' placeholder='用户名' required autofocus />\
						<input name='password' class='form-control' type='password' placeholder='密码' required />\
						<label id='loginRemember'><input type='checkbox'>&nbsp;记住用户</label>\
						<button class='btn btn-lg btn-success btn-block' type='submit'><span class='glyphicon glyphicon-log-in'></span>&nbsp;登陆</button>\
						<div class='login-link clearfix'>\
							<a id='registerDialog' class='pull-left' href='javascript:void(0)'>注册用户</a>\
							<a id='resetDialog' class='pull-right' href='javascript:void(0)'>重置密码</a>\
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
		$("#resetDialog").on("click",function(){
			createResetDialog();
		});
	}
	// 创建登出弹窗
	createLogoutDialog = function(data){
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
	// 发送验证码
	var sendVerifyCode = function(formSelector){
		if($(formSelector).validate().element(formSelector + " input[name='email']")) {
			$.post(registerUrl, {
				isGetVerifyCode: true,
				email : $(formSelector + " input[name='email']").val(),
			}, function(data, status){
				if (status == "success") {
					if (!data.isSuccess) {
						$(formSelector).prepend(getAlertTips("danger", data.tips));
						return;
					}
					// 提示验证码已发送
					$(formSelector).prepend(getAlertTips("info", "验证码已发至邮箱。"));
					// 更新验证码按钮
					var seconds = data.expires;
					$("#verifyCodeBtn").attr("disabled", true);
					$("#verifyCodeBtn").text("已发送(" + seconds + "s)");
					var intervalId = window.setInterval(function(){
						seconds--
						if (seconds > 0) {
							if ($("#verifyCodeBtn").length > 0) {
								$("#verifyCodeBtn").text("已发送(" + seconds + "s)");
							}
						}else{
							window.clearInterval(intervalId);
							if ($("#verifyCodeBtn").length > 0) {
								$("#verifyCodeBtn").attr("disabled", false);
								$("#verifyCodeBtn").text("获取验证码");
							}
						}
					}, 1000);
				} else {
					alert("注册失败！")
				}
			});
		}
	}
	// 创建注册弹窗
	createRegisterDialog = function(){
		// 创建弹窗
		createDialogPage("<form id='registerForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>PyToolsIP用户注册</h2>\
						<input name='name' class='form-control' type='text' placeholder='用户名' required autofocus />\
						<input id='password' name='password' class='form-control' type='password' placeholder='密码' required />\
						<input name='verifyPwd' class='form-control' type='password' placeholder='确认密码' required />\
						<input name='email' class='form-control' type='text' placeholder='邮箱' required />\
						<div class='input-group'>\
							<input name='verifyCode' class='form-control' type='text' placeholder='验证码' />\
							<span class='input-group-btn'>\
								<button id='verifyCodeBtn' class='btn btn-default' type='button'>获取验证码</button>\
							</span>\
						</div>\
						<button class='btn btn-lg btn-success btn-block' type='submit'><span class='glyphicon glyphicon-registration-mark'></span>&nbsp;注册</button>\
					</form>");
		// 绑定登陆按钮的点击校验事件
		$("#registerForm").validate({
			rules: {
				name: {
					required: true,
					rangelength: [2, 10],
					remote: {
						url : registerUrl,
						type : "post",
						dataType: "json",
						data : {
							isVerify : true,
							uname : function() {
								return $("#registerForm input[name='name']").val();
							},
						},
					},
				},
				password: {
					required: true,
					rangelength: [6, 16],
				},
				verifyPwd: {
					required: true,
					equalTo: "#password"
				},
				email: {
					required: true,
					email: true,
					remote: {
						url : registerUrl,
						type : "post",
						dataType: "json",
						data : {
							isVerify : true,
							email : function() {
								return $("#registerForm input[name='email']").val();
							},
						},
					},
				},
				verifyCode : "required",
			},
			messages: {
				name: {
					required: "请输入用户名",
					rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
					remote: "用户名已存在！请重新输入",
				},
				password: {
					required: "请输入密码",
					rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
				},
				verifyPwd: {
					required: "请输入确认密码",
					equalTo: "确认密码和密码不匹配"
				},
				email: {
					required: "请输入邮箱",
					email: "邮箱格式有误",
					remote: "邮箱已被注册！请使用新邮箱",
				},
				verifyCode : "请输入验证码",
			},
			submitHandler : function() {
				$.post(registerUrl, {
					isReq : true,
					email : email,
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#registerForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						$.post(registerUrl, {
							isRegister : true,
							uname : $("#registerForm input[name='name']").val(),
							upwd : eval(data.encodePwd.replace(/\$1/, $("#registerForm input[name='password']").val())),
							email : $("#registerForm input[name='email']").val(),
							verifyCode : $("#registerForm input[name='verifyCode']").val(),
						}, function(data, status){
							if (status == "success") {
								if (!data.isSuccess) {
									$("#registerForm").prepend(getAlertTips("danger", data.tips));
									return;
								}
								// 创建注册成功的弹窗
								createIntervalDialog("<h2>注册成功!</h2>", 2);
							} else {
								alert("注册失败！")
							}
						});
					}
				});
			},
		});
	    // 获取验证码
	    $("#verifyCodeBtn").on("click",function(){
			sendVerifyCode("#registerForm");
		});
	}
	// 创建更新密码弹窗
	createResetDialog = function(){
		// 创建弹窗
		createDialogPage("<form id='resetPwdForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>PyToolsIP更新密码</h2>\
						<input id='password' name='password' class='form-control' type='password' placeholder='新密码' required />\
						<input name='verifyPwd' class='form-control' type='password' placeholder='确认密码' required />\
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
		$("#resetPwdForm").validate({
            rules: {
                password: {
                    required: true,
                    rangelength: [6, 16],
                },
                verifyPwd: {
                    required: true,
                    equalTo: "#password"
                },
                email: {
                    required: true,
                    email: true,
					remote: {
						url : registerUrl,
						type : "post",
						dataType: "json",
						data : {
							isVerify : true,
							isExist: true,
							email : function() {
								return $("#registerForm input[name='email']").val();
							},
						},
					},
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
                    equalTo: "确认密码和密码不匹配"
                },
                email: {
                    required: "请输入邮箱",
                    email: "邮箱格式有误",
					remote: "邮箱未注册！",
                },
                verifyCode: {
                	required: "请输入验证码",
                }
            },
            submitHandler: function() {
				$.post(registerUrl, {
					isReq : true,
					email : email,
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#resetPwdForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						$.post(registerUrl, {
							isResetPwd : true,
							upwd : eval(data.encodePwd.replace(/\$1/, $("#resetPwdForm input[name='password']").val())),
							email : $("#resetPwdForm input[name='email']").val(),
							verifyCode : $("#resetPwdForm input[name='verifyCode']").val(),
						}, function(data, status){
							if (status == "success") {
								if (!data.isSuccess) {
									$("#resetPwdForm").prepend(getAlertTips("danger", data.tips));
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
       });
	   // 获取验证码
	   $("#verifyCodeBtn").on("click",function(){
		   sendVerifyCode("#resetPwdForm");
	   });
	}
	
//	// 定时弹窗
//	if ($('.jumbotron').length > 0) {
//		createIntervalDialog("<h2>定时弹窗</h2><p>测试...</p>", 5);
//	}
})