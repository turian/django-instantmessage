/*
 * TODO: overflow: scroll or dragging implementation for inbox container,
 * TODO: dostrings.
 */

var EVENT_ONLINE = 0,
    EVENT_OFFLINE = 1;

$(document).ready(function() {
    $("#messageform").live("submit", function() {
        im.sendMessage($(this));
        return false;
    }).live("keypress", function(event) {
        if (event.keyCode === 13) {
            im.sendMessage($(this));
            return false;
        };
    });

    $(window).unload(function() { im.sendEvent(EVENT_OFFLINE); });
    $("#message").focus();
    $.ajaxSetup({dataType: "json",
                 error: im.error});

    im.sendEvent(EVENT_ONLINE);
    im.sync();
});

var im = {
    timer: null,
    errorDelay: null,

    sync: function() {
        window.clearTimeout(im.timer);

        $.get(IM_SYNC_URL, 
              function(messages) {
                  im.errorDelay = null;
                  $.map(messages.payload, im.showMessage);
              });
        im.timer = window.setTimeout(im.sync, IM_SYNC_DELAY);
    },
    error: function() {
        im.errorDelay = (im.errorDelay) 
            ? im.errorDelay * 2
            : IM_SYNC_DELAY;

        $("#messageform :submit").removeAttr("disabled");
        im.timer = window.setTimeout(im.sync, im.errorDelay);
    },
    sendEvent: function(event) {
        $.post(IM_SEND_URL, {"event": event});
    },
    sendMessage: function(form) {
        form.find(":submit").attr("disabled", "disabled");

        $.post(IM_SEND_URL, form.serialize(), 
               function(message) { 
                   im.showMessage(message.payload);
                   form.find(":submit").removeAttr("disabled");
                   form.find(":text").val("").focus();
               });
        
    },
    showMessage: function(message) { $("#inbox").append(message); } 
};