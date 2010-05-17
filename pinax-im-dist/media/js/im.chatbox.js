/* 
 * Know issues: userlist state is reset, after the update. I.e. if you have friends / users
 * lists expaneded, they will be collapsed. This is the result of the server-side rendering.
 */

$(document).ready(function() {
    $("#chatbox #titlebar").click(function() { 
        var userlist = $(this).next("#userlist");
        userlist && userlist.toggle(); 
    });
    $("#chatbox .header").live("click", function() {
        var header = $(this);
        header.find(".expanded, .collapsed").toggle();
        header.children("ul").toggle();
    });

    $("#chatbox .user").live("click", chatbox.requestChat);
    $(".ui-notification .decline, .ui-notification-close").live("click", chatbox.declineChat);
    $(".ui-notification .accept").live("click", chatbox.acceptChat);

    $.ajaxSetup({
        dataType: "json",

        beforeSend: function() { $("#chatbox .updating").show(); },
        complete: function() { $("#chatbox .updating").hide(); }
    });

    chatbox.sync();

    $.noticeAdd.templates["im"] = "<div class='ui-notification'><div class='ow'><div class='iw'><div class='ui-notification-titlebar'><span class='ui-notification-title'></span><span class='ui-notification-close'>x</span></div><div class='ui-notification-content'></div></div></div></div>";
});

var chatbox = {
    timer: {},
    cache: {},
    visible: {},
    
    /* 
     * Shortcut function, initializes server polling for both users and
     * chat requests.
     * 
     * Arguments: none
     */
    sync: function() {
        chatbox.syncUsers();
        chatbox.syncRequests();
    },

    /* 
     * Function polls the server for a list of online users. The update only
     * occurs, if recieved data differs from the one, already displayed. This 
     * is determined, by comparing hashes of the displayed and recieved 
     * userlists. 
     * 
     * Arguments: none
     */
    syncUsers: function() {
        clearTimeout(chatbox.timer.users);
        
        $.get(IM_SYNC_URLS.users,
              function(response) { 
                  if (chatbox.cache.users !== response.hash) {
                      chatbox.cache.users = response.hash;
                      $("#userlist").replaceWith(response.payload);

                      // Updating user counter accordingly.
                      $("#counter").text($("#userlist .header li").length);
                  }
              });

        chatbox.timer.users = setTimeout(arguments.callee, 
                                         IM_SYNC_DELAY.users);
    },

    /* 
     * Function polls the server for new chat requests. Each chat request
     * is then displayed in a notification popup, with type value, corresponding
     * to it's state.
     * 
     * Arguments: none
     */
    syncRequests: function() {
        clearTimeout(chatbox.timer.requests);

        $.get(IM_SYNC_URLS.requests,
               function(response) {
                   for (var idx in response.payload) {
                       var request = response.payload[idx],
                           // Each recieved chat request will have an id
                           // of form <state>_<id>, thus we can get request
                           // state from the id attribute's value.
                           state = $(request).attr("id").split("_")[0];
                       chatbox.notify(request, state);
                   };
               });

        chatbox.timer.requests = setTimeout(arguments.callee, 
                                            IM_SYNC_DELAY.requests);
    },

    /* 
     * Shortcut function for $.notifyAdd, creates a popup notification, 
     * using the passed text string and type; the latter is later used 
     * for the class attribute of the created notification.
     * 
     * Arguments:
     * - text: notification message
     * - type: notification type, defaults to "request"
     */
    notify: function(text, type) {
        type = type || "request";
        $.noticeAdd({
            type: type,
            stay: ["request", "accepted"].indexOf(type) !== -1,
            duration: 5000,
            title: "chat " + type,
            position: "bottom-left",
            text: text,
            template: "im"
        });
    },

    /* 
     * Function sends a chat request, using target's href attribute for
     * the url. If successfull, notification popup, containing response 
     * data is displayed.
     * 
     * Arguments:
     * - event: reference to the fired event object
     */
    requestChat: function(event) { 
        $.post(event.target.href, function(response) {
            response.payload && chatbox.notify(response.payload, "info");
        });
        return false;
    },

    /* 
     * Function sends a reply to the incoming chat request; reply url is 
     * extracted from the target's href attribute. After the reply is 
     * delivered the corresponding notification popup is closed. 
     * 
     * Arguments:
     * - target: reference to the link, with the reply url
     * - accept: if true, then new chat window will be opened, as soon, as 
     *           the reply is delivered (with reply data used as window url)
     */
    sendReply: function(target, accept) {
        $.post(target.href, function(response) {
            accept && chatbox.open_chat(response.payload);
            $(target).closest(".iw").find(".ui-notification-close").click();
        });                           
        return false;
    },

    /* 
     * Shortcut functions for chatbox.sendReply. 
     * 
     * Arguments:
     * - event: reference to the fired event object (click-event object is 
     *          being passed, actually)
     */
    declineChat: function(event) { return chatbox.sendReply(event.target); },
    acceptChat: function(event) { return chatbox.sendReply(event.target, true); },

    /* 
     * Function pops up a new window with a given chat url, and displays the 
     * notification, in case the browser blocks the pop up.
     * 
     * Arguments:
     * - url: created chat url address
     */
    open_chat: function(url) { 
        if (!window.open(url, 
                         url.replace(/\//g, "_"), 
                         "width=500,height=300")) {
        // Firefox will most likely block the popup, so open a notification 
        // with chat url.
        chatbox.notify("Look's like your browser has just blocked the chat popup. " +
                       "You can still join the chatroom by following <a href='javascript" +
                       ":chatbox.open_chat(\"" + url + "\")>this</a> link.", "info");
        }
    }
};