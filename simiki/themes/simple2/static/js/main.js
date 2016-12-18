/*jslint browser: true*/
/*global $, jQuery, alert, console*/
$(document).ready(function () {
  "use strict";

  $('.list_wrapper').each(function(idx, obj) {
    var width = $(obj).children().eq(0).width() + 3;
    $(obj).children().eq(1).css({
      'margin-left': width
    });
  });

});
