/* ImChat object, implements chat IO handling.
 * Arguments:
 * - content: reference to chat content div
 * - input  : reference to text input element
 * 
 * Events:
 * - im.beforesync
 * - im.aftersync
 * - im.message.recieved
 * - im.message.sent
 */
function ImChat(content, input) {
    var timer = null;

    // Default event types, if you want to add more you need to
    // explicitly change theese, however it's recommeneded, that
    // 0 and 1 is left reserved for online / offline.
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

        // Auto offline message will be sent, if the user leaves the chat page.
        $(window).bind("unload",
            function(event) { 
                send(null, EVENT_OFFLINE, false);
            }).bind("im.message.sent", sync);

        // Sending presence.
        send(null, EVENT_ONLINE);

        // Setting up AJAX defaults.
        $.ajaxSetup({dataType: "json"});
    };

    /* Function queries the server for new messages and appends 
     * them to the content div.
     */
    function sync() {
        $(window).trigger("im.beforesync");

        // If the function was called from send(), we need to 
        // explicitly clear the timer.
        timer && clearTimeout(timer);
            
        $.ajax({
            method: "GET",
            url: IM_SYNC_URL,
            mode: "sync",
            success: function(messages) {
                for (var idx in messages) {
                    var message = messages[idx];
                    $(window).trigger("im.message.recieved", message);

                    content.append(message).animate({
                        scrollTop: content.attr("scrollHeight")
                    }, 500);
                };

                $(window).trigger("im.aftersync", messages.length);
            }
        });

        // Reinitilizing sync timer.
        timer = setTimeout(arguments.callee, IM_SYNC_DELAY);
    };

    /* Function extracts input value and sends it to the server, 
     * syncronizing the content on success.
     */
    function send(text, event, async) {
        text = text || input.val().trim();
        event = (event === undefined) ? null : event;
        async = (async === undefined) ? true : async;
        // Empty messages aren't sent to the server.
        if (text || event in [EVENT_ONLINE, EVENT_OFFLINE]) {
            $.ajax({
                type: "POST",
                mode: "sync",
                async: async,
                url: IM_SEND_URL, 
                data: {text: text, event: event},
                success: function(hash) { 
                    async && $(window).trigger("im.message.sent", hash); 
                }
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

