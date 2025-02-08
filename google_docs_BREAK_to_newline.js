function replaceBreakWithLineBreak() {
  // Open the active document
  var doc = DocumentApp.getActiveDocument();
  var body = doc.getBody();

  // Search for all occurrences of "<BREAK>"
  var searchResult = body.findText("<BREAK>");

  while (searchResult !== null) {
    // Get the text element containing the search result
    var element = searchResult.getElement();
    var start = searchResult.getStartOffset();
    var end = searchResult.getEndOffsetInclusive();

    // Replace "<BREAK>" with a line break
    element.deleteText(start, end);
    element.insertText(start, '\n');

    // Continue searching for the next occurrence
    searchResult = body.findText("<BREAK>", searchResult);
  }

  // Save the changes
  doc.saveAndClose();
}
