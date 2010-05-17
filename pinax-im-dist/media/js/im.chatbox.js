/* Function opens a new chat window with a given url
 * as window.location.
 */
function chat(url, user) {
    if (!window.open(url, 
                     url.replace(/\//g, "_"), 
                     "width=500,height=300")) {
        // Firefox will most likely block the popup, so open a notification 
        // with chat url.
        $.noticeAdd({
            duration: 5000,
            type: "im_declined",
            title: "success",
            template: "im",
            text: "Look's like your browser has just blocked the chat popup. " +
                  "You can still join the chatroom by following <a href='javascript:chat(\"" + 
                  url + "\")>this</a> link.",
            position: "bottom-left"});
    };
}

function ChatBox(element) {
    var header = $(".im_header", element), 
        userlist = $(".im_userlist", element).data("filter", true),
        updating = $(".im_updating", element),
        filter = $("#im_filter", element),
        visible_counter = $("#im_visible_count", element),
        all_counter = $("#im_all_count", element),
        timer = null;

    var REQUEST_READY = 0,
        REQUEST_ACCEPTED = 1,
        REQUEST_DECLINED = 2;

    /* Function initializes chatbox instance, by attaching click and 
     * update handlers to header, filter and userlist blocks.
     */
    function init() {
        header.click(
            function(event) { 
                if (userlist.children().length) {
                    header.nextAll("*").toggle();
                }
            });

        filter.click(
            function(event) {
                // Preventing the browser from following the link.
                event.preventDefault();
                
                // Updating userlist filter state.
                userlist.data("filter", !userlist.data("filter"));

                // Reinitilizing the userlist items.
                userlist.trigger("im.userlist.changed");

                // Not the most usable way of informing the user of the
                // filter state, but better than nothing anyway :)
                (userlist.data("filter")) 
                    ? filter.find("strong").text("+")
                    : filter.find("strong").text("-");
            });

        userlist.bind("im.userlist.changed",
            function() {
                var users = userlist.children("li");
                // If we have "display_all" filter disabled (thus only friends
                // should be displayed in the list), hiding added non-friend users
                // and updating visible users counter with a number of friends online
                if (!userlist.data("filter")) {
                    users.filter(".im_user").hide();
                    visible_counter.text(users.filter(".im_friend").length);
                } else {
                    users.filter(".im_user").show();
                    // Updating visible users counter with a number of total users 
                    // online, since no filtering involved.
                    visible_counter.text(users.length);
                }
                
                // Updating total online users counter.
                all_counter.text(users.length);

                // Binding click event to user items.
                users.children("a").click(
                    function(event) {
                        event.preventDefault();
                        $.post(this.href, "json");
                    });

                // If we have zero online an users and chat blocks are expaned, 
                // hiding them.
                if (!users.length && userlist.is(":visible")) {
                    userlist.trigger("im.userlist.empty");
                };
            }).bind("im.userlist.empty", function() { header.nextAll("*").hide(); });

        // Setting up updating image display on each request to the server.
        $.ajaxSetup({
             beforeSend: function() { updating.show(); },
             complete: function() { updating.hide(); },
             error: function() {
                 // Displaying the error notification.
                 $.noticeAdd({
                     duration: 5000,
                     type: "im_declined", // It just happend we have the red box 
                                          // already there for the declined message.
                     title: "error",
                     template: "im",
                     text: "Oops, something went wrong...",
                     position: "bottom-left"
                 });
             },
             dataType: "json"
         });

        // Requesting initial data from the server.
        sync();
    };

    /* Function requests user and online users data from the 
     * server 
     */
    function sync() {
        // If the function was called from request(), we need to explicitly
        // clear the timer.
        timer && clearTimeout(timer);

        $.getJSON(IM_SYNC_URL, 
                  function(data) {
                      sync_users(data);
                      sync_requests(data);
                      userlist.trigger("im.userlist.changed"); // Redrawing the box.
                  });

        // Reinitilizing sync timer.
        timer = setTimeout(arguments.callee, IM_SYNC_DELAY);
    };

    /* Function updates userlist with the data recieved from the 
     * server 
     */
    function sync_users(data) { 
        userlist
            .empty()
            .append(data.online.join("")); 
    };

    /* Function handles incoming request data, displating the 
     * appropriate notification for requests with a different 
     * state value.
     */
    function sync_requests(data) {
        var types = ["request", "accepted", "declined"];

        for (idx in data.requests) {
            (function(request) {
                 var notice = $.noticeAdd({
                     duration: 5000,
                     stay: !(request.state === REQUEST_DECLINED),
                     title: "chat " + types[request.state],
                     template: "im",
                     text: request.content,
                     type: "im_" + types[request.state],
                     position: "bottom-left"
                 });

                 notice.find("a").click(
                     function(event) {
                         if (this.id.match(/accept|decline/)) {
                             // After the user accept a chat request, chat window
                             // is opened.
                             var callback = (this.id.match(/accept/))
                                 ? (function(data) { data && chat(data.url); }) 
                                 : null;
                             
                             event.preventDefault();
                             $.post(this.href, 
                                    {hash: request.hash},
                                    callback);
                         }

                         // Hiding notice block.
                         $.noticeRemove(notice);
                     });
             })(data.requests[idx]);
        };
    };

    // Initializing chatbox instance;
    init();
}

$(document).ready(
    function() {
        $.noticeAdd.templates["im"] = "<div class='ui-notification'><div class='ow'><div class='iw'><div class='ui-notification-titlebar'><span class='ui-notification-title'></span><span class='ui-notification-close'>x</span></div><div class='ui-notification-content'></div></div></div></div>";
        new ChatBox($(".im_box"));
    });