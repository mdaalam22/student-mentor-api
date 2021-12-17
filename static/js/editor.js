var script1 = document.createElement('script');
script1.type = 'text/javascript';
script1.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-svg.js";
document.head.appendChild(script1);


var link2 = document.createElement('link');
link2.rel = "stylesheet";
link2.type = "text/css"
link2.href = "https://cdn.quilljs.com/1.3.6/quill.snow.css";
document.head.appendChild(link2);

var script2 = document.createElement('script');
script2.type = 'text/javascript';
script2.src = "https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.min.js";
document.head.appendChild(script2);

// var script3 = document.createElement('script');
// script3.type = 'text/javascript';
// script3.src = "https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.core.min.js";
// document.head.appendChild(script3);

script2.onload = function(){
var quill = new Quill('.vLargeTextField', {
    placeholder: 'Click the MathJax button to insert a formula.',
    theme: 'snow',
    modules: {
      toolbar: [
          ['bold', 'italic', 'underline', 'strike'],
          ['link'],
          ['blockquote'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'script': 'sub'}, { 'script': 'super' }], 
          ['align', { 'align': 'center' }, { 'align': 'right' }, { 'align': 'justify' }]
      ]
    },
  });

}

