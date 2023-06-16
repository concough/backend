$(document).ready(function () {
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });
    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    var dropable = $(".dropable");
    var progress = $(".progress");
    var progress_bar = $(".progress-bar");
    var pnl_f = $(".upload-huge .panel-footer");

    progress.hide();

    $("#fileupload").fileupload({
        dataType: 'json',
        sequentialUploads: true,
        dropZone: dropable,
        drop: function (e, data) {
            console.log(e);
            if (data.files.length > 0) {
                $.each(data.files, function (index, file) {
                    pnl_f.append('<span class="text-primary">' + file.name + '</span><br>');
                });
            }
        },
        start: function (e) {
            progress.show();
            progress_bar.css({"width": "0%"}).text("0%");
        },
        stop: function (e) {
            setTimeout(function () {
                progress.fadeOut();
            }, 1500);
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            progress_bar.css({"width": strProgress}).text(strProgress);
        },
        done: function (e, data) {
            const status = data.result.status;
            if (status === "OK") {
                const r = data.result.data;

                var templ = '<span class="img_container"><span class="img_order"><span class="label label-info">'
                    + r.img_order
                    + '</span></span><img class="img-sel img-thumbnail" src="'
                    + r.img_url
                    + '" width="60" style="margin-left: 15px;" data-toggle="modal" data-target="#pictureModal" data-picture="'
                    + r.img_url
                    + '" data-qs="'
                    + r.qno
                    + '" data-imgorder="'
                    + r.img_order
                    + '"><a href="'
                    + r.delete_link
                    + '" class="img_del"><span class="glyphicon glyphicon-remove"></span></a></span>';

                $('tr[data-qid="' + r.qid + '"] td:nth-child(2)').append(templ)

            }
        }
    });
});