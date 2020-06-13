  $(document).ready(function () {
    var quill = new Quill('#editor-container', {
    modules: {
        syntax: true,
      toolbar: [
        [{'header': [1, 2, 3, 4, 5, 6, false]}],
        [{'size': ['small', false, 'large', 'huge']}],
        [{'font': [] }],
        ['bold', 'italic', 'underline', 'strike'],
        ['link', 'blockquote', 'code-block', 'image', 'video'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{'script': 'sub'}, {'script': 'super'}],
        [{'indent': '-1'}, {'indent': '+1'}],
        [{'direction': 'rtl'}],
        [{'color': [] }, {'background': [] }],
        [{'align': [] }],
      ]
    },
    placeholder: 'Compose an epic...',
    theme: 'snow'
  });

    var form = document.getElementById("writeArticleForm");
    form.onsubmit = function() {
    // Populate hidden form on submit
    var articleBody = document.querySelector('input[name=articleBody]');
    var html = document.querySelector(".ql-editor").innerHTML;
    articleBody.value = html;
    // No back end to actually submit to!
    return true;
  }
});