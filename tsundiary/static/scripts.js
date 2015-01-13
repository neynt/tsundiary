
// Writing script. Automatically pushes changes to server.

var save_timer = -1;
window.dc_check_interval = -1;
window.old_content = null;
window.cur_date = "";
window.last_timestamp = null;
var last_write_time = 0;
var start_write_time = 0;

var CHAR_LIMIT = 10000;

function currently_writing() {
  return (new Date().getTime() - last_write_time < 3000)
}

// Received response from server after confession.
function confession_response(data) {
  response = JSON.parse(data);
  // saved!
  $('#save_status').html(response['message']);
  clearTimeout(dc_check_interval);
  last_timestamp = response['timestamp'];
}

// Posts current entry to the server.
function confess() {
    $('#save_status').html('saving...');
    content = textarea.val();
    clearTimeout(dc_check_interval);
    dc_check_interval = setTimeout(function() {
        $('#save_status').html('disconnected? <a id="tryagain">try again</span>');
        $('#tryagain').click(confess);
    }, 8000);
    $.post('/confess', { content: content, cur_date: cur_date },
        confession_response);
}

function prime_update() {
    $('#save_status').html('writing...')
    last_write_time = new Date().getTime();
    if (save_timer == -1) {
      start_write_time = new Date().getTime();
    }
    if (new Date().getTime() - start_write_time > 5000) {
      // Save every 5 seconds, even if the user is still typing.
    }
    clearTimeout(save_timer);
    save_timer = setTimeout(function() {
        confess();
        save_timer = -1;
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
        if (!currently_writing()) {
            if ('datestamp' in data) {
                if (data['datestamp'] != cur_date) {
                  // automatically reload at 4am, when day flips over
                  location.reload(true);
                }
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

    update_char_count();
}

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

// Make "hide/unhide" buttons work.

function toggle_post_hidden(post_date, hide_button) {
  $.post('/toggle_post_hidden', { post_date: post_date }, function(data) {
    d = JSON.parse(data);
    if (d['entry_hidden']) {
      hide_button.addClass('activated_control');
    }
    else {
      hide_button.removeClass('activated_control');
    }
  });
}

window.bind_post_controls = function () {
  $('.post_controls').each(function (index) {
    var controls = $(this);
    var hide_button = controls.children('.hide_button');
    hide_button.click(function () {
      toggle_post_hidden(controls.parent().parent().data('date'), hide_button);
    });
  });
};

// Stuff to do on a new page
InstantClick.on('change', function (isInitialLoad) {
    //update_char_count();
    bind_post_controls();
    if ('textarea' in window) {
      update_char_count();
      textarea.focus();
    }
});
