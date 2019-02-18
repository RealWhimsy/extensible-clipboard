package org.libreoffice.example.dialog;

import java.io.File;
import java.io.FileWriter;
import java.io.FileOutputStream;
import java.io.IOException;

import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DocumentHelper;

import com.sun.star.beans.XPropertySet;
import com.sun.star.text.XText;
import com.sun.star.text.XTextContent;
import com.sun.star.text.XTextCursor;
import com.sun.star.text.XTextDocument;
import com.sun.star.text.XTextViewCursor;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;

public class DataHelper {
	
	private static File createTemporaryFileFromEntry(ClipEntry entry) {
		try {
			File tmpFile = File.createTempFile("LOC2", "");
			if (entry.getData() != null) {
				FileWriter fw = new FileWriter(tmpFile);
				fw.write(entry.getData());
				fw.close();
			}
			else {
				FileOutputStream fos = new FileOutputStream(tmpFile);
				fos.write(entry.getBinData());
				fos.close();
			}			
			return tmpFile;
		} catch (IOException e) {
			return null;
		}
	}
	
	private static void insertGraphicFromFile(XComponentContext xContext, File tmpFile) {
		 com.sun.star.lang.XMultiComponentFactory xMCF = xContext.getServiceManager();
			// Querying for the interface XTextDocument on the xcomponent
         XTextDocument xTextDoc = DocumentHelper.getCurrentDocument(xContext);
         // Querying for the interface XMultiServiceFactory on the xtextdocument
         com.sun.star.lang.XMultiServiceFactory xMSFDoc =
             UnoRuntime.queryInterface(
             com.sun.star.lang.XMultiServiceFactory.class, xTextDoc);

         Object oGraphic = null;
         try {
             // Creating the service GraphicObject
             oGraphic =xMSFDoc.createInstance("com.sun.star.text.TextGraphicObject");
         }
         catch ( Exception exception ) {
             System.out.println( "Could not create instance" );
         }

         // Getting the text
         XText xText = xTextDoc.getText();

         // Getting the cursor on the document
         XTextCursor xTextCursor = xText.createTextCursor();

         // Querying for the interface XTextContent on the GraphicObject
         XTextContent xTextContent =
             UnoRuntime.queryInterface(
             XTextContent.class, oGraphic );

         // Printing information to the log file
         try {
             // Inserting the content
             xText.insertTextContent(xTextCursor, xTextContent, true);
         } catch ( Exception exception ) {
             System.out.println( "Could not insert Content" );
             exception.printStackTrace(System.err);
         }

         // Printing information to the log file

         // Querying for the interface XPropertySet on GraphicObject
         XPropertySet xPropSet =
             UnoRuntime.queryInterface(
             XPropertySet.class, oGraphic);
         try {
             // Creating a string for the graphic url
             StringBuffer sUrl = new StringBuffer("file:///");
             sUrl.append(tmpFile.getCanonicalPath().replace('\\', '/'));
             System.out.println( "insert graphic \"" + sUrl + "\"");

             com.sun.star.graphic.XGraphicProvider xGraphicProvider =
                 UnoRuntime.queryInterface(com.sun.star.graphic.XGraphicProvider.class,
                     xMCF.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",
                     xContext));


             com.sun.star.beans.PropertyValue[] aMediaProps = new com.sun.star.beans.PropertyValue[] { new com.sun.star.beans.PropertyValue() };
             aMediaProps[0].Name = "URL";
             aMediaProps[0].Value = sUrl;

             com.sun.star.graphic.XGraphic xGraphic =
                 UnoRuntime.queryInterface(com.sun.star.graphic.XGraphic.class,
                             xGraphicProvider.queryGraphic(aMediaProps));

             // Setting the anchor type
             xPropSet.setPropertyValue("AnchorType",
                        com.sun.star.text.TextContentAnchorType.AT_PARAGRAPH );

             // Setting the graphic url
             xPropSet.setPropertyValue( "Graphic", xGraphic );

             // Setting the horizontal position
             xPropSet.setPropertyValue( "HoriOrientPosition",
                                        Integer.valueOf( 5500 ) );

             // Setting the vertical position
             xPropSet.setPropertyValue( "VertOrientPosition",
                                        Integer.valueOf( 4200 ) );

             // Setting the width
             xPropSet.setPropertyValue( "Width", Integer.valueOf( 4400 ) );

             // Setting the height
             xPropSet.setPropertyValue( "Height", Integer.valueOf( 4000 ) );
         } catch ( Exception exception ) {
             System.out.println( "Couldn't set property 'GraphicURL'" );
         }
		
	}

	public static void insertIntoGUICursor(XComponentContext xContext, ClipEntry entry) {
		String mt = entry.getMimetype();
		
		if (mt.contains("text/")) {
			XTextViewCursor xViewCursor = DocumentHelper.getCurrentCursor(xContext);
			XText xCrsrText = xViewCursor.getText();
			XTextCursor xDocumentCursor = xCrsrText.createTextCursorByRange(xViewCursor.getStart());
			xDocumentCursor.gotoRange(xViewCursor.getEnd(), true);
			//TODO Problem when trying to set HTML-String
			xDocumentCursor.setString(entry.getData().toString());
		}
		else if (mt.contains("image/")) {
			// https://api.libreoffice.org/examples/java/Text/GraphicsInserter.java
			System.out.println("Inserting graphic");
			File tmpFile = createTemporaryFileFromEntry(entry);
			insertGraphicFromFile(xContext, tmpFile);
            tmpFile.delete();
		}
	}
	
	public static XText getCurrentGUISelection(XComponentContext xContext) {
		XTextViewCursor xViewCursor = DocumentHelper.getCurrentCursor(xContext);
		XText xCrsrText = xViewCursor.getText();
		return xCrsrText;
	}
}
