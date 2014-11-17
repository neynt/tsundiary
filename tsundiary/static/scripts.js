
// Writing script. Automatically pushes changes to server.

var save_timer = null;
window.update_interval = null;
window.old_content = null;
var cur_date = "{{ g.date.strftime('%Y%m%d') }}";
window.last_timestamp = null;
var writing = false;

var CHAR_LIMIT = 10000;

function confess() {
    $('#save_status').html('saving...');
    content = textarea.val();
    $.post('/confess', { content: content, cur_date: cur_date },
        function (data) {
            d = JSON.parse(data);
            $('#save_status').html(d['message']);
            last_timestamp = d['timestamp'];
            //$('#num_entries').html(d['num_entries']);
            console.log('last timestamp updated to ', last_timestamp);
            writing = false;
        }
    );
}

function prime_update() {
    $('#save_status').html('writing...')
    writing = true;
    save_timer = setTimeout(function() {
        $('#save_status').html('saving...')
        confess();
    }, 500);
}

function update_char_count() {
    var count = unescape(encodeURIComponent(textarea.val())).length;
    if (count > 0) {
        $('#char_count').html(count);
    } else {
        $('#char_count').html('&nbsp;');
    }

    // Scale textarea
    var orig_scroll = $(document).scrollTop();
    textarea.css("height", "5em");
    textarea.css("height", textarea[0].scrollHeight + "px");
    $(document).scrollTop(orig_scroll);

    return count;
}

window.content_changed = function() {
    var count = update_char_count();
    update_char_count();
    clearTimeout(save_timer);

    if (count <= CHAR_LIMIT) {
        //$('#char_count').removeClass('error');
        old_content = textarea.val();
    }
    else {
        //$('#char_count').addClass('error');
        //$('#save_status').html('too long');
        textarea.val(old_content);
        update_char_count();
    }
    prime_update();
}

window.get_updates = function() {
    $.getJSON('/api/my_current_entry', function(data) {
        if (!writing) {
            if ('datestamp' in data) {
                cur_date = data['datestamp'];
            }
            var mydate = new Date(data['timestamp']*1000);
            var myts = mydate.getTime()/1000;
            if (myts > last_timestamp + 0.5) {
                $('#edit_area').val(data['content']);
                $('#save_status').html('synced!');
                last_timestamp = myts;
                update_char_count();
            }
        }
    });
}

InstantClick.on('change', function (isInitialLoad) {
    update_char_count();

});

//window.onload = function () {
//    update_char_count();
//    textarea.bind('input propertychange', content_changed);
//    setInterval(get_updates, 1000);
//};


// Infinite scrolling script.
// Currently unused.

var processScroll = true;
var last_date = '{{ posts[-1].posted_date }}';
function proc_scroll () {
    if (processScroll && $(window).scrollTop() > $(document).height() - $(window).height() - 1000) {
        processScroll = false;
        $.get('/+{{ author.sid }}/' + last_date,
          function (data) {
            new_post = $(data)
            last_date = new_post.data('date');
            if (last_date) {
              $('#posts').append(new_post);
              processScroll = true;
              proc_scroll(); // If this wasn't enough, load even more!
            }
          }
        );
    }
}
/*
$(window).scroll(proc_scroll);
proc_scroll();
*/
