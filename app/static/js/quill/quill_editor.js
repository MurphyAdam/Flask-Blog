$(document).ready(function () {
  var quill = new Quill('#editor-container-pp', {
  modules: {
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

  var form = document.getElementById("writePrivacyPolicyForm");
  form.onsubmit = function() {
  // Populate hidden form on submit
  var privacyPolicyBody = document.querySelector('input[name=privacyPolicyBody]');
  var html = document.querySelector(".ql-editor").innerHTML;
  privacyPolicyBody.value = html;
  // No back end to actually submit to!
  return true;
}
});