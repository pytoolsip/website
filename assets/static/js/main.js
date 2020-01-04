$(function(){
	// 更新footer的位置
	updateFooterPosition = function() {
		if ($(window).height() > $("body").height()) {
			$("footer").css({position:"fixed", bottom:0});
		} else {
			$("footer").css({position:"static", bottom:0});
		}
	};
	// 监听窗口尺寸大小变化
	(function(){
		var windowOnresizeFunc = window.onresize; // 响应窗口尺寸大小变化函数
		window.onresize = function(){
			if (windowOnresizeFunc != null) {
				windowOnresizeFunc();
			}
			updateFooterPosition();
		}
		updateFooterPosition();
	})();

	$(".carousel").carousel();
	$("#toTop").on("click",function(){
		$('body,html').animate({scrollTop:0},280);
	});
	// 首页链接
	var HOME_URL = "http://localhost:8008";
	// 用户信息链接
	var userInfoUrl = HOME_URL+"/userinfo";
	// 登陆链接
	var loginUrl = userInfoUrl + "?k=login";
	// 注册链接
	var registerUrl = userInfoUrl + "?k=register";
	// 公钥
	var PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYeNBCn22B90arUKX7Tmgrg6dVZN20e+6u+KChIByh/ozfVJkL21xx36tcLdnKH0TFHu5HEVlo7TonUGSuQZoYRNvCprWIdf9SHwlID1pm3/D3ZrAQsVPmEZUharShAEqGe1fkOPzzRfae/MIwvrZji1RSgzCW69kMTv/70+wXIQIDAQAB-----END PUBLIC KEY-----";
	// 编码字符串
	encodeStr = function(s) {
		var ec = new JSEncrypt();
		ec.setPublicKey(PUBLIC_KEY);
		return ec.encrypt(s);
	}
	// 获取提示文档
	var getAlertTips = function(type, tips) {
		return "<div class='alert alert-"+ type +"' role='alert'>\
			<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\
			<span class='alertContent'>"+ tips +"</span>\
		</div>";
	}
    // 获取用户登录信息
    var checkIsLogined = function(){
		return $.cookie("is_logined") == "logined";
	}
	// 登陆平台
    loginIP = function(formId, callback){
		var name = $("#"+formId+" input[name='name']").val();
		var pwd = $("#"+formId+" input[name='password']").val();
		var isRemember = $("#loginRemember>input[type='checkbox']").is(":checked");
		$.post(loginUrl, {
			isLogin : true,
			uname : name,
			upwd : encodeStr(pwd),
			isRemember : isRemember,
		}, function(data, status){
			if (status == "success") {
				if (!data.isSuccess) {
					$("#"+formId).prepend(getAlertTips("danger", data.tips));
					return;
				}
				console.log("登陆成功。");
				// 登陆成功回调
				callback();
			} else {
				alert("登陆失败！")
			}
		});
    }
	// 登出平台
    logoutIP = function(formId, callback){
		$.post(loginUrl, {
			isLogout : true,
		}, function(data, status){
			if (status == "success") {
				if (!data.isSuccess) {
					if (formId != null) {
						$("#"+formId).prepend(getAlertTips("danger", data.tips));
					}
					return;
				}
				console.log("登出成功。");
				// 登出成功回调
				callback();
			} else {
				alert("登出失败！")
			}
		});
    }
	// 关闭弹窗
	closeDialogPage = function(){
		if ($('#dialogPage').length > 0) 	{
			$('#dialogPage').remove();
		}
	}
	// 创建弹窗函数[带有关闭回调参数]
	createDialog = function(content, closeCallback, sizeClass="col-md-12"){
		// 关闭原有弹窗
		closeDialogPage();
		// 弹窗内容
		var dialogPage = "<div id='dialogPage'>\
			<div class='container'>\
				<div class='row'>\
					<div class='dialog-background "+ sizeClass +"'>\
						<a id='closeDialogPage' href='javascript:void(0);' title='关闭弹窗'><span class='glyphicon glyphicon-remove'></span>关闭</a>\
						<div class='dialog-content'>" + content + "</div>\
					</div>\
				</div>\
			</div>\
		</div>";
		// 添加弹窗
		$("body").append(dialogPage);
		// 更新弹窗页尺寸方法
		function updateDialogPageSize(){
			if ($('#dialogPage').length > 0) {
				var pageWidth = Math.max($(window).width(), $("body").width());
				$('#dialogPage').width(pageWidth);
				var pageHeight = Math.max($(window).height(), $("body").height());
				$('#dialogPage').height(pageHeight);
				// 移动到弹窗中心
				$('body,html').animate({scrollLeft : (pageWidth - $(window).width())/2, scrollTop: (pageHeight - $(window).height())/2}, 0);
			}
		}
		updateDialogPageSize();
		// 监听窗口尺寸变化方法
		var windowOnresizeFunc = window.onresize;
		window.onresize = function(){
			if (windowOnresizeFunc != null) {
				windowOnresizeFunc();
			}
			updateDialogPageSize();
		}
		// 点击关闭的事件
		$("#closeDialogPage").on("click",function(){
			// 移除弹窗页
			closeDialogPage();
			// 重置窗口大小事件
			window.onresize = windowOnresizeFunc;
			// 回调关闭函数
			closeCallback();
		});
	}
	// 创建弹窗函数
	createDialogPage = function(content, sizeClass="col-md-4 col-md-offset-4"){
		createDialog(content, function(){}, sizeClass); // 关闭弹窗时无回调
	}
	// 创建定时弹窗
	createIntervalDialog = function(content, seconds, closeCallback){
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
			closeCallback();
		});
	}
	// 创建登录弹窗
	var createLoginDialog = function(){
		// 新建登陆Socket
		var loginWs = createLoginSocket(function(ws) {
			$("#qrCodeLoginImg").attr("src", "");
		});
		// 创建弹窗
		createDialog("<form id='loginForm' class='login-form' role='form' enctype='multipart/form-data'>\
						<h2>登陆PyToolsIP</h2>\
						<ul id='loginNavTabs' class='nav nav-tabs nav-justified' role='tablist'>\
							<li role='presentation' class='active'><a href='#pwdLogin' role='tab' data-toggle='tab'>账号登陆</a></li>\
							<li role='presentation'><a href='#qrCodeLogin' role='tab' data-toggle='tab'>二维码登陆</a></li>\
						</ul>\
						<div class='tab-content'>\
							<div id='pwdLogin' class='tab-pane fade in active login-form' style='margin-top: 30px;'>\
								<input name='name' class='form-control' type='text' placeholder='用户名' required autofocus />\
								<input name='password' class='form-control' type='password' placeholder='密码' required />\
								<label id='loginRemember'><input type='checkbox'>&nbsp;记住用户</label>\
								<button class='btn btn-lg btn-success btn-block form-control' type='submit'><span class='glyphicon glyphicon-log-in'></span>&nbsp;登陆</button>\
							</div>\
							<div id='qrCodeLogin' class='tab-pane fade login-form' style='margin: 30px 0px;'>\
								<div class='qrCodeContent'>\
									<div class='qrCodeContentItem hidden' data-target='valid' style='margin: 40px 0px;'>\
										<img id='qrCodeLoginImg' class='center-block' src='' alt='正在刷新二维码' width='80%' />\
										<p class='text-center' style='margin-top: 20px;color: #ABABAB;font-size: 10px;'>*&nbsp;请打开【APP】，在【我的】页中点击扫描二维码。</p>\
									</div>\
									<div class='qrCodeContentItem hidden' data-target='invalid' style='margin: 100px 0px;'>\
										<p class='text-center' style='margin: 20px 0px;color: #686868;'><span class='glyphicon glyphicon-warning-sign'></span>二维码已过期！</p>\
										<button id='qrCodeUpdateBtn' class='btn btn-md btn-default center-block' type='button'><span class='glyphicon glyphicon-refresh'></span>&nbsp;点击刷新</button>\
									</div>\
									<div class='qrCodeContentItem' data-target='loading' style='margin: 120px 0px;'>\
										<p class='text-center' style='color: #686868;font-size: 14px;'><span class='glyphicon glyphicon-repeat'></span>正在加载二维码...</p>\
									</div>\
								</div>\
							</div>\
						</div>\
						<div class='login-link clearfix'>\
							<a id='registerDialog' class='pull-left' href='javascript:void(0)'>注册用户</a>\
							<a id='resetDialog' class='pull-right' href='javascript:void(0)'>重置密码</a>\
						</div>\
					</form>", function() {
						loginWs.close(); // 关闭socket
					});
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
				loginIP("loginForm", function(){
					// 关闭socket
					loginWs.close();
					// 关闭弹窗
					closeDialogPage();
				});
			}
		});
		// 初始化登陆事件
		initLoginEvent(loginWs);
	}
	// 初始化登陆页面元素的相关时间
	initLoginEvent = function(loginWs){
		// 更新二维码的内容
		var updateQrCodeContent = function(key) {
			$("#qrCodeLogin .qrCodeContentItem").each(function(){
				if ($(this).attr("data-target") == key) {
					if ($(this).hasClass("hidden")) {
						$(this).removeClass("hidden");
					}
				} else {
					if (!$(this).hasClass("hidden")) {
						$(this).addClass("hidden");
					}
				}
			});
		};
		// 处理二维码函数
		loginWs.respQrcode = function(qrcode, expires){
			updateQrCodeContent("valid");
			$("#qrCodeLoginImg").attr("src", "data:image/png;base64," + qrcode);
			window.setTimeout(function() {
				$("#qrCodeLoginImg").attr("src", "");
				updateQrCodeContent("invalid");
			}, expires*1000);
		};
		// 绑定注册超链接的点击事件
		$("#registerDialog").on("click",function(){
			loginWs.close(); // 关闭socket
			createRegisterDialog();
		});
		// 绑定更新密码超链接的点击事件
		$("#resetDialog").on("click",function(){
			loginWs.close(); // 关闭socket
			createResetDialog();
		});
		// 切换loginNavTabs
		$("#loginNavTabs li").on("click", function(){
			if ($(this).hasClass("active")) {
				return;
			}
			if ($(this).find("a").attr("href") == "#qrCodeLogin") {
				if ($("#qrCodeLoginImg").attr("src") == "") {
					loginWs.reqQrcode();
					updateQrCodeContent("loading");
				}
			}
		});
		// 点击刷新二维码按钮
		$("#qrCodeUpdateBtn").on("click", function(){
			loginWs.reqQrcode();
			updateQrCodeContent("loading");
		});
		// 判断当前是否正在二维码的标签页
		if ($("#loginNavTabs a").attr("href") == "#qrCodeLogin") {
			loginWs.reqQrcode();
			updateQrCodeContent("loading");
		}
	};
	// 创建用户信息弹窗
	var createUserInfoDialog = function(data){
		// 创建弹窗
		createDialogPage("<div id='userinfoContent' class='userinfoContent'>\
							<h2 class='text-center'>用户信息</h2>\
							<ul id='userInfoTab' class='nav nav-tabs nav-justified' role='tablist'>\
								<li role='presentation' class='active'><a href='#showUserInfo' role='tab' data-toggle='tab'>展示信息</a></li>\
								<li role='presentation'><a href='#changeUserInfo' role='tab' data-toggle='tab'>更改信息</a></li>\
							</ul>\
							<div class='tab-content'>\
								<div id='showUserInfo' class='tab-pane fade in active'>\
									<div class='tab-pane-sub'>\
										<h5 class='text-center'>基础信息</h5>\
										<p>用户名：<span>" + data.name + "</span></p>\
										<p>邮箱：<span>" + data.email + "</span></p>\
									</div>\
									<div class='tab-pane-sub'>\
										<h5 class='text-center'>扩展信息</h5>\
										<p>\
											头像：\
											<img class='img-thumbnail img-responsive' src='" + data.img + "' alt='用户头像' style='width: 60px;height: 60px; border-radius: 6px;'/>\
										</p>\
										<p>个性签名：<span>" + data.bio + "</span></p>\
									</div>\
									<button id='logoutButton' class='btn btn-default btn-block' type='button' style='margin-top:30px;'><span class='glyphicon glyphicon-log-out'></span>&nbsp;退出账号</button>\
								</div>\
								<div id='changeUserInfo' class='tab-pane fade'>\
									<div class='tab-pane-sub'>\
										<h5 class='text-center'>基础信息</h5>\
										<div class='input-group'>\
											<label class='input-group-addon' for='newName'>用户名</label>\
											<input name='newName' type='text' placeholder='" + data.name + "' class='form-control' readOnly>\
											<div class='input-group-btn'>\
												<button type='button' class='btn btn-default changeButton' data-target='newName'>更改</button>\
											</div>\
										</div>\
										<div class='input-group'>\
											<label class='input-group-addon' for='newEmail'>邮箱</label>\
											<input name='newEmail' type='text' placeholder='" + data.email + "' class='form-control' readOnly>\
											<div class='input-group-btn'>\
												<button type='button' class='btn btn-default changeButton' data-target='newEmail'>更改</button>\
											</div>\
										</div>\
										<div class='input-group'>\
											<label class='input-group-addon' for='newPwd'>密码</label>\
											<input name='newPwd' type='text' placeholder='****************' class='form-control' readOnly>\
											<div class='input-group-btn'>\
												<button type='button' class='btn btn-default changeButton' data-target='newPwd'>更改</button>\
											</div>\
										</div>\
									</div>\
									<div class='tab-pane-sub'>\
										<form id='changeUserInfoForm' role='form' enctype='multipart/form-data' method='POST'>\
											<h5 class='text-center'>扩展信息</h5>\
											<div class='input-group'>\
												<label class='input-group-addon' for='uname'>头像</label>\
												<div class='input-group-btn' style='padding:0;'>\
													<div style='width: 36px;height: 36px;'>\
														<img class='img-thumbnail img-responsive' src='" + data.img + "' alt='用户头像'/>\
													</div>\
												</div>\
												<input type='file' name='newImg' class='form-control' accept='.png,.jpg' onchange='javascript:void(0);'>\
											</div>\
											<div class='input-group'>\
												<label class='input-group-addon' for='bio'>个性签名</label>\
												<textarea name='newBio' class='form-control' rows='4'>" + data.bio + "</textarea>\
											</div>\
											<button type='submit' class='form-control btn btn-success'><span class='glyphicon glyphicon-refresh'></span>&nbsp;更新扩展信息</button>\
										</form>\
									</div>\
								</div>\
							</div>\
							<div class='modal fade' role='dialog' data-backdrop='false'>\
								<div class='modal-dialog' role='document'>\
									<div id='changeUserBasicInfo' class='modal-content'>\
									</div>\
								</div>\
							</div>\
						</div>");
		// 显示提示
		var showAlert = function(item, type, text) {
			if (item == null) {
				item = $("#userinfoContent");
			}
			item.prepend("<div class='alert alert-"+ type +"' role='alert'>\
					<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\
					<span class='alertContent'>"+ text +"</span>\
				</div>");
		}
		// 绑定注销按钮的点击事件
		$("#logoutButton").on("click",function(){
			logoutIP(null, function(){
				// 关闭弹窗
				closeDialogPage();
				// 创建登陆弹窗
				createLoginDialog();
			});
		});
		// 更新用户信息
		$("#changeUserInfoForm").validate({
            submitHandler: function() {
				if (!checkIsLogined()) {
					createLoginDialog();
					return;
				}
				var $form = $("#changeUserInfoForm");
				addInputsToForm($form, [
					{"key":"isChange", "val":"true", "type":"text"},
				]);
				// 提交数据
				$.ajax({
					url : userInfoUrl+"?k=detail",
					type : "post",
					data : new FormData($form[0]),
					processData : false,
					contentType : false,
					success : function(data){
						if (data.isSuccess) {
							createUserInfoDialog(data);
							showAlert(null, "success", data.tips || "更改成功。");
						} else {
							showAlert(null, "danger", data.tips || "更改失败，请重试！");
						}
					},
					error: function(e) {
						console.log(e);
						showAlert(null, "danger", "更改失败，请重试！");
					}
				});
            }
		});
		// 点击更改按钮回调函数
		var onClickChangeBtn = function(dt) {
			// 显示modal
			$("#userinfoContent .modal").modal("show");
			// 显示弹窗
			var data = {name: dt, title: "", type: "text", placeholder: "", pwdLabel: "请输入密码进行确认", tips: ""};
			var extInput = "";
			if (dt == "newName"){
				data.title = "更改用户名";
				data.placeholder = "请输入新用户名";
			}else if (dt == "newEmail"){
				data.title = "更改邮箱";
				data.placeholder = "请输入新邮箱";
			}else if (dt == "newPwd"){
				data.title = "更改密码";
				data.type = "password";
				data.placeholder = "请输入新密码";
				data.pwdLabel = "请输入旧密码进行确认";
				extInput = "<input name='verifyPwd' type='password' placeholder='请再次输入新密码' class='form-control'>";
			}
			var content = "\
				<div class='modal-header'>\
					<button type='button' class='close' data-dismiss='modal' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\
					<h3 class='modal-title'>"+ data.title +"</h3>\
				</div>\
				<form id='changeUserBasicInfoForm' class='modal-body' role='form' enctype='multipart/form-data' method='POST'>\
					<input id='" + data.name + "' name='" + data.name + "' type='" + data.type + "' placeholder='" + data.placeholder + "' class='form-control'>\
					"+ extInput +"\
					<input name='password' type='password' placeholder='" + data.pwdLabel + "' class='form-control'>\
					<button type='submit' class='btn btn-warning form-control'>确定"+ data.title +"</button>\
				</form>\
				<div class='modal-footer'>\
					<p>"+ data.tips +"</p>\
				</div>";
			$("#changeUserBasicInfo").html(content);
			// 提交更新内容
			$("#changeUserBasicInfoForm").validate({
				rules: {
					newName: {
						required: true,
						rangelength: [2, 10],
						remote: {
							url : registerUrl,
							type : "post",
							dataType: "json",
							data : {
								isVerify : true,
								uname : function() {
									return $("#changeUserBasicInfoForm input[name='newName']").val();
								},
							},
						},
					},
					mewEmail: {
						required: true,
						email: true,
						remote: {
							url : registerUrl,
							type : "post",
							dataType: "json",
							data : {
								isVerify : true,
								email : function() {
									return $("#registerForm input[name='mewEmail']").val();
								},
							},
						},
					},
					newPwd: {
						required: true,
						rangelength: [6, 16],
					},
					verifyPwd: {
						required: true,
						equalTo: "#newPwd"
					},
					password: {
						required: true,
					},
				},
				messages: {
					newName: {
						required: "请输入新用户名",
						rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
						remote: "用户名已存在！请重新输入",
					},
					mewEmail: {
						required: "请输入新邮箱",
						email: "邮箱格式有误",
						remote: "邮箱已被注册！请使用新邮箱",
					},
					newPwd: {
						required: "请输入新密码",
						rangelength: $.validator.format("请输入介于{0}和{1}长度的值"),
					},
					verifyPwd: {
						required: "请再次输入新密码",
						equalTo: "确认密码和密码不匹配"
					},
					password: {
						required: "请输入确认密码",
					},
				},
				submitHandler: function(form) {
					if (!checkIsLogined()) {
						createLoginDialog();
					} else {
						var pwd = $("#changeUserBasicInfoForm input[name='password']").val();
						var sendData = {
							isBase: true,
							isChange: true,
							upwd : encodeStr(pwd),
						};
						sendData[data.name] = $("#changeUserBasicInfoForm input[name='"+ data.name +"']").val();
						if (data.name == "newPwd") {
							sendData[data.name] = encodeStr(sendData[data.name]);
						}
						$.post(userInfoUrl+"?k=detail", sendData, function(data, status){
							if (status == "success" && data.isSuccess) {
								createLoginDialog();
								if (data.tips != "") {
									showAlert($("#loginForm"), "success", (data.tips || "更改成功。") + "请重新登陆。");
								}
							} else {
								showAlert($("#changeUserBasicInfo"), "danger", data.tips || "更改失败，请重试！");
							}
						});
					}
				}
			});
		}
		$(".changeButton").on("click", function(){
			onClickChangeBtn($(this).attr("data-target"));
		})
	}
	// 点击用户事件
	$("#user").on("click",function(){
		if (!checkIsLogined()) {
			createLoginDialog();
		} else {
			$.post(userInfoUrl+"?k=detail", {}, function(data, status){
				if (status == "success" && data.isSuccess) {
					createUserInfoDialog(data);
				} else {
					createLoginDialog();
				}
			});
		}
	});
    // 添加input到form中
    var addInputToForm = function(item, name, value, type){
        var $input = item.find("input[name='" + name + "']");
        if ($input.length > 0) {
            $input.val(value);
            if ($input.attr("type") != type) {
                $input.attr("type", type)
            }
        } else {
            item.append("<input name='" + name + "' class='hidden' type='" + type + "' value='" + value + "' />");
        }
    }
    // 添加数据到表单
    addInputsToForm = function(item, exIpts){
        // 添加扩展输入
        if (exIpts instanceof Array && exIpts.length > 0) {
            for (var i = 0; i < exIpts.length; i++) {
                var ipt = exIpts[i];
                addInputToForm(item, ipt.key, ipt.val, ipt.type);
            }
        }
    }
	// 请求文章/工具详情表单
	requestArticleDetailForm = function(form, exIpts, callback){
		if (!checkIsLogined()) {
			createLoginDialog();
			return;
		}
		addInputsToForm(form, exIpts);
        // 提交数据
        $.ajax({
            url : window.location.href,
            type : "post",
            data : new FormData(form[0]),
            processData : false,
            contentType : false,
            success : function(data){
                callback(data);
            },
            error: function(e) {
                console.log(e);
                alert("提交表单失败！");
            }
        })
	};
	// 请求收藏文章/工具详情
	requestCollectArticle = function(data, callback){
		if (!checkIsLogined()) {
			createLoginDialog();
			return;
		}
		$.post(window.location.href, data, function(resp, status){
			if (status == "success" && resp.isLoginFailed) {
				createLoginDialog();
			} else {
				callback(resp, status);
			}
		});
	};
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
	var createRegisterDialog = function(){
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
				var uname = $("#registerForm input[name='name']").val();
				var upwd = $("#registerForm input[name='password']").val();
				$.post(registerUrl, {
					isRegister : true,
					uname : uname,
					upwd : encodeStr(upwd),
					email : $("#registerForm input[name='email']").val(),
					verifyCode : $("#registerForm input[name='verifyCode']").val(),
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#registerForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						// 创建注册成功的弹窗
						createIntervalDialog("<h2>注册成功!</h2><p>即将跳转登陆界面...</p>", 2, function(){
							// 创建登陆界面
							createLoginDialog();
							$("#loginForm input[name='name']").val(uname);
							$("#loginForm input[name='password']").val(upwd);
						});
					} else {
						alert("注册失败！")
					}
				});
			}
		});
	    // 获取验证码
	    $("#verifyCodeBtn").on("click",function(){
			sendVerifyCode("#registerForm");
		});
	}
	// 创建更新密码弹窗
	var createResetDialog = function(){
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
								return $("#resetPwdForm input[name='email']").val();
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
					isResetPwd : true,
					upwd : encodeStr($("#resetPwdForm input[name='password']").val()),
					email : $("#resetPwdForm input[name='email']").val(),
					verifyCode : $("#resetPwdForm input[name='verifyCode']").val(),
				}, function(data, status){
					if (status == "success") {
						if (!data.isSuccess) {
							$("#resetPwdForm").prepend(getAlertTips("danger", data.tips));
							return;
						}
						// 创建登录成功的弹窗
						createIntervalDialog("<h2>密码更新成功!</h2><p>即将跳转登陆界面...</p>", 2, function(){
							// 创建登陆界面
							createLoginDialog();
						});
					} else {
						alert("注册失败！")
					}
				});
			}
		});
	   // 获取验证码
	   $("#verifyCodeBtn").on("click",function(){
		   sendVerifyCode("#resetPwdForm");
	   });
	}

	// 显示关于弹窗
	$("#aboutDzjH").on("click", function(){
		// 创建弹窗
		createDialogPage("<div>\
		<style>\
			a, a:link {\
				color: #868686;\
			}\
			a:visited{\
				color: #989898;\
			}\
			a:hover{\
				color: #686868;\
			}\
			.content-text p {\
				text-align:left;\
				padding: 0px;\
				margin: 0px;\
				text-indent:2em;\
				line-height:30px;\
			}\
			.content-ex-text {\
				text-align:center;\
				color: #989898;\
				padding-top: 30px;\
				border-top: 1px #DCDCDC solid;\
			}\
		</style>\
		<h2 style='color:black;padding-bottom:20px;'>关于<strong style='color:#0b487e'>梦心DH</strong></h2>\
		<div class='content-text' style='padding: 20px 10px'>\
			<p>本网站是基于<strong>个人兴趣</strong>而制作的，主要目的是为了将自己平时一些想法或见闻，以程序或其他方式进行实现，最终集合到该网站。</p>\
			<p>这个网站的设计及其内容，可能杂揉了我的许多个人主观思想。当你发现存在奇怪或者不合理的地方时，请通过<strong>邮件联系</strong>，并一起探讨合适设计方式或结果。</p>\
			<p>而我仅作为一名开发者，对于思考问题的方式，有时难免会走进自己都没意识到的误区之中。再加上我自身的开发经验和实力，都还太少、太弱，因此设计出来的作品也许并不总让人满意。所以，如果可以的话，希望能得到你们的指导，与我一起完善这个网站及相关内容。</p>\
			<p>谢谢。</p>\
		</div>\
		<div class='content-ex-text'>\
			<span>联系方式：15602291936</span>\
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
			<span>邮箱：15602291936@163.com</span>\
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
			<span>GitHub：<a href='https://github.com/JDreamHeart' title='JDreamHeart'>https://github.com/JDreamHeart</a></span>\
		</div>\
		</div>", "col-md-8 col-md-offset-2");
	});
	
//	// 定时弹窗
//	if ($('.jumbotron').length > 0) {
//		createIntervalDialog("<h2>定时弹窗</h2><p>测试...</p>", 5);
//	}
})