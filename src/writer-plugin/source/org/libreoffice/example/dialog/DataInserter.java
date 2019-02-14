package org.libreoffice.example.dialog;

import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DocumentHelper;

import com.sun.star.text.XPageCursor;
import com.sun.star.text.XText;
import com.sun.star.text.XTextCursor;
import com.sun.star.text.XTextDocument;
import com.sun.star.text.XTextViewCursor;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;

public class DataInserter {

	public static void insertIntoGUICursor(XComponentContext xContext, String entry) {
		System.out.println("Inserting entry");
		XTextDocument xText = DocumentHelper.getCurrentDocument(xContext);
		System.out.println(xText.getText().getString());
		XTextViewCursor xViewCursor = DocumentHelper.getCurrentCursor(xContext);
		XPageCursor xPageCursor = (XPageCursor)UnoRuntime.queryInterface(
		          XPageCursor.class, xViewCursor);
		System.out.println("The current page number is " + xPageCursor.getPage());
		XText xCrsrText = xViewCursor.getText();
		XTextCursor xDocumentCursor = xCrsrText.createTextCursorByRange(xViewCursor.getStart());
		xDocumentCursor.gotoRange(xViewCursor.getEnd(), true);
		xDocumentCursor.setString(entry);
	}
}
