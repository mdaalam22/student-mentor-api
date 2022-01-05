function getChapter(course_id) {
    let $ = django.jQuery;
    $.get('/course/chapter-list/' + course_id, function (resp){
        let chapter_list = '<option value="" selected="">---------</option>'
        $.each(resp.data, function(i, item){
           chapter_list += '<option value="'+ item.id +'">'+ item.chapter_title +'</option>'
        });
        $('#id_chapter').html(chapter_list);
    });
}
