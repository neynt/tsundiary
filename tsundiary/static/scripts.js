// Writing script. Automatically pushes changes to server.

// Timeout used for automatic saving.
var save_timeout = -1;

// Timeout used to detect when user has disconnected.
// (POST, and no response within 8000 seconds.)
window.disconnected_timeout = -1;

// The current date, in the format YYYYMMDD. Don't judge.
window.cur_date = "";

// Last timestamp received from confessing to the server.
window.last_timestamp = null;

// Time user last typed something.
var last_write_time = 0;

// Time since user started typing.
var start_write_time = 0;

// Sent a confession and have not received a response from server.
var confessing = false;

var CHAR_LIMIT = 10000;

// User entered something and it should eventually be sent to the server.
function prime_update() {
  $('#save_status').html('writing...');
  last_write_time = new Date().getTime();
  if (save_timeout == -1) {
    start_write_time = new Date().getTime();
  }
  if (last_write_time - start_write_time < 4500) {
    clearTimeout(save_timeout);
    save_timeout = setTimeout(function() {
      confess();
      save_timeout = -1;
    }, 500);
  }
}

// Posts current entry to the server.
function confess() {
  confessing = true;
  $('#save_status').html('saving...');
  var content = textarea.val();
  clearTimeout(window.disconnected_timeout);
  window.disconnected_timeout = setTimeout(function() {
    $('#save_status').html('disconnected. <a id="tryagain">try again</span>');
    $('#tryagain').click(confess);
  }, 8000);
  $.post('/confess', { content: content, cur_date: cur_date },
  confession_response);
}

// Received response from server after confess().
function confession_response(data) {
  response = JSON.parse(data);
  // "saved!" ... hopefully
  $('#save_status').html(response['message']);
  clearTimeout(window.disconnected_timeout);
  last_timestamp = response['timestamp'];
  confessing = false;
}

function update_char_count() {
  var count = unescape(encodeURIComponent(textarea.val())).length;
  if (count == 0) {
    $('#char_count').html('&nbsp;');
  } else if (count > CHAR_LIMIT) {
    $('#char_count').html(count + '/' + CHAR_LIMIT);
  } else {
    $('#char_count').html(count);
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

  if (count <= CHAR_LIMIT) {
    $('#char_count').removeClass('error');
    prime_update();
  }
  else {
    $('#char_count').addClass('error');
    $('#save_status').html('too long!');
    update_char_count();
  }
}

function should_accept_sync() {
  // User typed something in the last 3 sec.
  if ((new Date().getTime() - last_write_time < 3000)) {
    return false;
  }
  // User POSTed an update and has not received a response yet.
  if (confessing) {
    return false;
  }
  return true;
}

window.get_updates = function() {
  $.getJSON('/api/my_current_entry', function(data) {
    if (should_accept_sync()) {
      if ('datestamp' in data) {
        if (data['datestamp'] != cur_date) {
          // automatically reload at 4am, when day flips over
          location.reload(true);
        }
      }

      var mydate = new Date(data.timestamp * 1000);
      var myts = mydate.getTime() / 1000;
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
    var len = textarea.val().length;
    textarea[0].setSelectionRange(len, len);
  }
});
