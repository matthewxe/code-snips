const editor = ace.edit("ace-editor", {
	minLines: 15,
	maxLines: 40,
	theme: "ace/theme/one_dark",
	fontFamily: "Fira Code",
});

const modelist = ace.require("ace/ext/modelist");
const filename = document.getElementById("filename");
filename.addEventListener("input", function() {
	const filePath = filename.value;
	const mode = modelist.getModeForPath(filePath).mode;
	editor.session.setMode(mode); // mode now contains "ace/mode/javascript".
});

const tab_size = document.getElementById("tabSize");
tab_size.addEventListener("input", function() {
	editor.session.setTabSize(tab_size.value);
});

document.getElementById("form").onsubmit = () => {
	document.getElementById("submit_button").value = editor.getValue();
};
