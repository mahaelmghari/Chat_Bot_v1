$document.ready(function() {
  if(!window.console)window.console = {};
  if(!window.console.log)window.console.log = function(){};

  $("messageform").on("submit", function(){
    sendMsg($(this));
    return false;
  });

  $("messageform").on("keypress", function(e){
    if(e.which == 13){
      sendMsg($(this));
      return false;
    }
    return true;
  });
  $("#message").select();
  updater.poll();
});

function newMessage(form) {
  var message = form.formToDict();
  var disabled = form.find("input[type=submit]");
  disabled.disable();
  $.postJSON("/a/message/new", message, function(response) {
    updater.showMessage(response);
    if(message.id) {
      form.parent().remove();
    } else {
      form.find("input[type=text]").val("").select();
      disabled.$enable();
    }
  });
}

function getCookie(name) {
  var r = document.cookie.match("(?:^|; )" + name + "=([^;]*)\\b");
  return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, data, callback) {
  args._xsrf = getCookie("_xsrf");
  $.ajax({url: url, data: $.param(args), dataType: "json", type: "POST",
    success:function(response) {
      if (callback) callback(eval ("(" + response + ")"));
    }, error:function(response) {
      console.log("ERROR");
    }
  });
};

jQuery.fn.formToDict = function() {
  var fields = this.serializeArray();
  var json = {};
  for (var i = 0; i < fields.length; i++) {
    json[fields[i].name] = fields[i].value;
  }
  if(json.next) delete json.next;
  return json;
};

jQuery.fn.disable = function() {
  this.enable(false);
  return this;
};

jQuery.fn.enable = function(opt_enable) {
  if(arguments.length && !opt_enable) {
    this.data("enable", false);
  } else {
    this.data("enable", true);
  } return this;
};

var updater = {
  errorSleepTime: 500,
  cursor: null,

  poll: function(){
    var args = {"_xsrf": getCookie("_xsrf")};
    if(updater.cursor) args.cursor = updater.cursor;
    $.ajax({url: "/a/message/updates", type: "POST", data: $.param(args), dataType: "text",
      data: $.param(args), success: updater.onSuccess, error: updater.onError});
  },
  
  onSuccess: function(response) {
    try {
      updater.newMessage(eval("(" + response + ")"));
    } catch(e) {
      updater.onError();
      return;
    }
    updater.errorSleepTime = 500;
    window.setTimeout(updater.poll, 0);
  },

  onError: function(response) {
    updater.errorSleepTime *= 2;
    console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
    window.setTimeout(updater.poll, updater.errorSleepTime);
  },

  newMessage: function(response) {
    if(!response.message) return;
    var messages = response.messages;
    updater.cursor = messages[messages.length - 1].id;
    console.log(messages.length, "new messages, cursor:", updater.cursor);
    for(var i=0; i < messages.length; i++) {
      updater.showMessage(messages[i]);
    }
  },

  showMessage: function(message) {
    var existing = $("#m" + message.id);
    if(existing.length > 0) return;
    var msg = $("<div class='message' id='m" + message.id + "'><span class='user'>" +
                message.user + "</span> <span class='body'></span></div>");
    msg.find(".body").text(message.body);
    $("#chat").append(msg);
    $("#chat")[0].scrollTop = $("#chat")[0].scrollHeight;
  }

};
