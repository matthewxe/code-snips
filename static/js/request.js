const editor = ace.edit("ace-editor", {
	minLines: 15,
	maxLines: 40,
	theme: "ace/theme/one_dark",
	fontFamily: "Fira Code",
	mode: "ace/mode/markdown",
});

const tab_size = document.getElementById("tabSize");
tab_size.addEventListener("input", function() {
	editor.session.setTabSize(tab_size.value);
});

document.getElementById("form").onsubmit = () => {
	document.getElementById("submit_button").value = editor.getValue();
};
