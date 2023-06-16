/**
 * Created by abolfazl on 5/24/15.
 */
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();

  $('#pictureModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var img_src = button.data('picture');
    var img_qs = button.data('qs');
    var img_order = button.data('imgorder');

    var modal = $(this);
    modal.find('.modal-title').text('سوال ' + img_qs + ' - ردیف ' + img_order);
    modal.find('.modal-body .big-img').attr('src', img_src);
  });
  $('#picQuoteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var img_src = button.data('picture');
    var img_t = button.data('title');

    var modal = $(this);
    modal.find('.modal-title').text(img_t);
    modal.find('.modal-body .big-img').attr('src', img_src);
  });

  $(".user-info").popover({
      content: function() {
            return $('.user-info-popover').html();
          }
  });

  $('#chooseTypist, #typedoneform, #checkdoneform, #checkdoneform2, #finalCost, #rejectform').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget);
      var tid = button.data('taskid');
      var eid = button.data('entranceid');
      var ttitle = button.data('task_title');

      var modal = $(this);
      modal.find('.modal-title').text(ttitle);

      modal.find('[name="job_unique_key"]').val(eid);
      modal.find('[name="task_unique_key"]').val(tid);
  });

  $('#payoffform, #payoffform2').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget);
      var user_id = button.data('user_id');
      var ttitle = button.data('title');

      var modal = $(this);
      modal.find('.modal-title').text(ttitle);
      modal.find('[name="user_id"]').val(user_id);
  });

  $('#chooseSupervisor').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget);
      var eid = button.data('entrance_id');
      var ttitle = button.data('title');

      var modal = $(this);
      modal.find('.modal-title').text(ttitle);
      modal.find('[name="entrance_id"]').val(eid);
  });

  $('input[data-action="auto-complete"]').on('input', function (e) {
      var text = $(this).val();
      if (text.length >= 3) {
          var area = $(this).data('ac-area');
          $('div#' + area).empty();

          var url = $(this).data('ac-url');
          var csrf = $(this).closest('form').find('[name="csrfmiddlewaretoken"]').first().val();

          $.post(url, {'title': text, 'csrfmiddlewaretoken': csrf}).done(function (data) {
              if (data.data.length > 0) {
                  $(data.data).each(function (index, value) {
                      $('div#' + area).append('<label class="btn btn-default"><input type="radio" name="options" id="' + value.id + '" value="' + value.id + '"/>&nbsp;' + value.title + "&nbsp;</label>");

                  });
              }
          }).fail(function () {

          });
      }
  });

});