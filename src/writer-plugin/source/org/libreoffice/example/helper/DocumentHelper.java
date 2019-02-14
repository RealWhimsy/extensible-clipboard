package org.libreoffice.example.helper;

import com.sun.star.frame.XController;
import com.sun.star.frame.XDesktop;
import com.sun.star.frame.XFrame;
import com.sun.star.frame.XModel;
import com.sun.star.lang.XComponent;
import com.sun.star.lang.XMultiComponentFactory;
import com.sun.star.text.XTextDocument;
import com.sun.star.text.XTextViewCursor;
import com.sun.star.text.XTextViewCursorSupplier;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.view.XViewCursor;

public class DocumentHelper {
	
	/** Returns the current XDesktop */
	public static XDesktop getCurrentDesktop(XComponentContext xContext) {
		XMultiComponentFactory xMCF = (XMultiComponentFactory) UnoRuntime.queryInterface(XMultiComponentFactory.class,
				xContext.getServiceManager());
        Object desktop = null;
		try {
			desktop = xMCF.createInstanceWithContext("com.sun.star.frame.Desktop", xContext);
		} catch (Exception e) {
			return null;
		}
        return (XDesktop) UnoRuntime.queryInterface(com.sun.star.frame.XDesktop.class, desktop);
	}
	
	/** Returns the current XComponent */
    private static XComponent getCurrentComponent(XComponentContext xContext) {
        return (XComponent) getCurrentDesktop(xContext).getCurrentComponent();
    }
    
    /** Returns the current frame */
    public static XFrame getCurrentFrame(XComponentContext xContext) {
    	XModel xModel = (XModel) UnoRuntime.queryInterface(XModel.class, getCurrentComponent(xContext));
    	return xModel.getCurrentController().getFrame();
    }

    /** Returns the current text document (if any) */
    public static XTextDocument getCurrentDocument(XComponentContext xContext) {
        return (XTextDocument) UnoRuntime.queryInterface(XTextDocument.class, getCurrentComponent(xContext));
    }
    
    /** Returns the cursor from the current loaded document 
     * https://wiki.openoffice.org/wiki/Documentation/DevGuide/Text/Example:_Visible_Cursor_Position
    */
    public static XTextViewCursor getCurrentCursor(XComponentContext xContext) {
    	XModel xModel = (XModel) UnoRuntime.queryInterface(XModel.class, getCurrentComponent(xContext));
    	XController xController = xModel.getCurrentController();
    	XTextViewCursorSupplier supplier = (XTextViewCursorSupplier) UnoRuntime.queryInterface(
    			XTextViewCursorSupplier.class, xController);
    	return supplier.getViewCursor();
    }
}
