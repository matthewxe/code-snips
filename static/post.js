var editor = ace.edit("ace-editor");
editor.setTheme("ace/theme/tomorrow_night");
editor.setOptions({
	maxLines: 10,
});

var language_select = document.getElementById("language");
language_select.addEventListener("input", function() {
	var selected = language_select.options[language_select.selectedIndex].value;
	editor.session.setMode("ace/mode/" + selected);
	var code = editor.getValue();
});
