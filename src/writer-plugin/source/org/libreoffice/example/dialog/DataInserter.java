package org.libreoffice.example.dialog;

import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DocumentHelper;

import com.sun.star.text.XText;
import com.sun.star.text.XTextCursor;
import com.sun.star.text.XTextViewCursor;
import com.sun.star.uno.XComponentContext;

public class DataInserter {

	public static void insertIntoGUICursor(XComponentContext xContext, ClipEntry entry) {
		/**
		 * Switch entry->mimetype to do action accoring to format
		 */
		XTextViewCursor xViewCursor = DocumentHelper.getCurrentCursor(xContext);
		XText xCrsrText = xViewCursor.getText();
		XTextCursor xDocumentCursor = xCrsrText.createTextCursorByRange(xViewCursor.getStart());
		xDocumentCursor.gotoRange(xViewCursor.getEnd(), true);
		//TODO Problem when trying to set HTML-String
		xDocumentCursor.setString(entry.getData().toString());
	}
}
