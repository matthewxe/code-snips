var editor = ace.edit("ace-editor", {
	maxLines: 10,
	theme: "ace/theme/tomorrow_night",
	fontFamily: "Fira Code",
});

var language_select = document.getElementById("language");
language_select.addEventListener("input", function() {
	var selected = language_select.options[language_select.selectedIndex].value;
	editor.session.setMode("ace/mode/" + selected);
});

var editor_max = document.getElementById("editorMax");
editor_max.addEventListener("input", function() {
	editor.setOptions({
		maxLines: editor_max.value,
	});
});

var tab_size = document.getElementById("tabSize");
tab_size.addEventListener("input", function() {
	editor.session.setTabSize(tab_size.value);
});

document.getElementById("form").onsubmit = () => {
	document.getElementById("submit_button").value = editor.getValue();
};
