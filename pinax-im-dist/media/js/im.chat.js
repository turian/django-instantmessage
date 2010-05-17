/* ImChat object, implements chat IO handling.
 * Arguments:
 * - content: reference to chat content div
 * - input  : reference to text input element
 */
function ImChat(content, input) {
    var updating = $(".im_updating"),
        timer = null;

    var EVENT_ONLINE = 0,
        EVENT_OFFLINE = 1;

    /* Function initializes ImChat object, attaching Enter and 
     * C-Enter handlers and requesting messages from the server.
     */
    function init() {
        input.keypress(    
            function(event) {
                // We are only interested in Enter events from the input
                // element. By default, pressing Enter forces message
                // sending, and C-Enter is used for linebreaks.
                if (event.keyCode === 13) {
                    if (!event.ctrlKey) {
                        event.preventDefault();
                        send();
                    } else { 
                        // Appending newline character to the input value.
                        input.val(input.val() + "\n");
                    };
                };
            });

        // Setting up updating image display on each request to the server.
        $.ajaxSetup({
             beforeSend: function() { updating.show(); },
             complete: function() { updating.hide(); },
             dataType: "json"
         });

        // Sending presence.
        send(null, EVENT_ONLINE);

        // Auto offline message will be sent, if the user leaves the chat page.
        $(window).bind("beforeunload",
                       function(event) { send(null, EVENT_OFFLINE); });
    };

    /* Function queries the server for new messages and appends 
     * them to the content div.
     */
    function sync() {
        // If the function was called from send(), we need to 
        // explicitly clear the timer.
        timer && clearTimeout(timer);
            
        $.get(IM_SYNC_URL,
              function(messages) {
                  for (idx in messages) {
                      content.append(messages[idx]);
                      content.animate({scrollTop: content.attr("scrollHeight")}, 500);
                  };
              });

        // Reinitilizing sync timer.
        timer = setTimeout(arguments.callee, IM_SYNC_DELAY);
    };

    /* Function extracts input value and sends it to the server, 
     * syncronizing the content on success.
     */
    function send(text, event, callback) {
        text = text || input.val().trim();
        event = (event === undefined) ? null : event;
        // Empty messages aren't sent to the server.
        if (text || event in [EVENT_ONLINE, EVENT_OFFLINE]) {
            $.post(IM_SEND_URL, 
                   {text: text,
                    event: event},
                   function() { 
                       // Executing the callback if it's present (can come in 
                       // handy for offline notification) and syncronizing with 
                       // the server.
                       callback && callback();
                       sync();
                   });
            
            // Emptying the input.
            text && input.val(""); 
        };
    };

    // Initializing chat instance;
    init();
}

$(document).ready(
    function() {
        new ImChat($(".im_chat"), $(".im_msgbox"));
    });

/* Function makes a pause for a given amount of time.
 * Source: http://docs.jquery.com/Cookbook/wait
 */
jQuery.fn.wait = function(time, type) {
        time = time || 1000;
        type = type || "fx";
        return this.queue(type, function() {
            var self = this;
            setTimeout(function() {
                $(self).dequeue();
            }, time);
        });
    };
