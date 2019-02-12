package org.libreoffice.example.dialog;

import org.libreoffice.example.helper.DialogHelper;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlModel;
import com.sun.star.awt.tree.XMutableTreeDataModel;
import com.sun.star.awt.tree.XMutableTreeNode;
import com.sun.star.beans.XPropertySet;
import com.sun.star.awt.tree.MutableTreeDataModel;
import com.sun.star.awt.XDialog;
import com.sun.star.awt.XDialogEventHandler;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.uno.Exception;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;


public class ActionOneDialog implements XDialogEventHandler {
	
	private XDialog dialog;
	private static final String actionOk = "actionOk";
	private String[] supportedActions = new String[] { actionOk };
	
	public ActionOneDialog(XComponentContext xContext) throws Exception{
		//https://forum.openoffice.org/en/forum/viewtopic.php?f=20&t=7348
		this.dialog = DialogHelper.createDialog("ActionOneDialog.xdl", xContext, this);
		XControl tree = DialogHelper.getTree(this.dialog, "ClipTree");
		XControlModel model = tree.getModel();
		//fillTree(tree, model);
		Object xTreeData = xContext.getServiceManager().createInstanceWithContext(
                "com.sun.star.awt.tree.MutableTreeDataModel", xContext);
		XMutableTreeDataModel mxTreeDataModel = (XMutableTreeDataModel) UnoRuntime.queryInterface(
           XMutableTreeDataModel.class, xTreeData);

		XMutableTreeNode xNode = mxTreeDataModel.createNode("Root", false);

		mxTreeDataModel.setRoot(xNode);
		XPropertySet xTreeModelProperty = (XPropertySet) UnoRuntime.queryInterface(
				XPropertySet.class, model);
		xTreeModelProperty.setPropertyValue("DataModel", mxTreeDataModel);
	}
	
	public void fillTree(XControl tree, XControlModel model) {
		System.out.println(tree);
		System.out.println(model);
		

	}

	public void show() {
		dialog.execute();
	}
	
	private void onOkButtonPressed() {
		dialog.endExecute();
	}
	
	@Override
	public boolean callHandlerMethod(XDialog dialog, Object eventObject, String methodName) throws WrappedTargetException {
		if (methodName.equals(actionOk)) {
			onOkButtonPressed();
			return true; // Event was handled
		}
		return false; // Event was not handled
	}

	@Override
	public String[] getSupportedMethodNames() {
		return supportedActions;
	}

}
