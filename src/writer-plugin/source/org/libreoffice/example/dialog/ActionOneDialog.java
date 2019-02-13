package org.libreoffice.example.dialog;

import java.util.Collection;
import java.util.List;

import org.libreoffice.example.clipboardapi.ClipboardServer;
import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DialogHelper;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlModel;
import com.sun.star.awt.tree.XMutableTreeDataModel;
import com.sun.star.awt.tree.XMutableTreeNode;
import com.sun.star.awt.XDialog;
import com.sun.star.awt.XDialogEventHandler;
import com.sun.star.beans.XPropertySet;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.uno.Exception;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;


public class ActionOneDialog implements XDialogEventHandler {
	
	private XComponentContext xContext;
	private XDialog dialog;
	private static final String actionOk = "actionOk";
	private static final String actionSync = "actionSync";
	private String[] supportedActions = new String[] { actionOk, actionSync };
	private ClipboardServer cbServer;
	
	public ActionOneDialog(XComponentContext xContext) throws Exception{
		this.xContext = xContext;
		this.dialog = DialogHelper.createDialog("ActionOneDialog.xdl", this.xContext, this);		
	}
	
	public void fillTree(Collection<ClipEntry> clips) throws Exception{
		//https://forum.openoffice.org/en/forum/viewtopic.php?f=20&t=7348
		XControl tree = DialogHelper.getTree(this.dialog, "ClipTree");
		XControlModel model = tree.getModel();
		
		Object xTreeData = this.xContext.getServiceManager().createInstanceWithContext(
                "com.sun.star.awt.tree.MutableTreeDataModel", this.xContext);
		XMutableTreeDataModel mxTreeDataModel = (XMutableTreeDataModel) UnoRuntime.queryInterface(
           XMutableTreeDataModel.class, xTreeData);

		XMutableTreeNode root = mxTreeDataModel.createNode("Clips", false);
		
		for (ClipEntry c : clips) {
			XMutableTreeNode parent = mxTreeDataModel.createNode(c.getData(), false);
			root.appendChild(parent);
			List<ClipEntry> children = c.getChildren();
			for (ClipEntry child : children) {
				XMutableTreeNode childNode = mxTreeDataModel.createNode(child.getData(), false);
				parent.appendChild(childNode);
			}
		}

		mxTreeDataModel.setRoot(root);
		XPropertySet xTreeModelProperty = (XPropertySet) UnoRuntime.queryInterface(
				XPropertySet.class, model);
		xTreeModelProperty.setPropertyValue("DataModel", mxTreeDataModel);
	}

	public void show() {
		dialog.execute();
	}
	
	private void onOkButtonPressed() {
		dialog.endExecute();
	}
	
	private void onSyncButtonPressed() {
		String url = DialogHelper.getEditField(dialog, "ServerUrlInput").getText();
		if ( cbServer == null) {
			cbServer = new ClipboardServer();
		}	
		if ( !cbServer.setServerURL(url) ) {
			System.out.println("Invalid url");
		}
		
		Collection<ClipEntry> clips = cbServer.getAllClips();
		try {
			System.out.println("in try");
			fillTree(clips);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	@Override
	public boolean callHandlerMethod(XDialog dialog, Object eventObject, String methodName) throws WrappedTargetException {
		if (methodName.equals(actionOk)) {
			onOkButtonPressed();
			return true; // Event was handled
		}
		if (methodName.equals(actionSync)) {
			onSyncButtonPressed();
			return true;
		}
		return false; // Event was not handled
	}

	@Override
	public String[] getSupportedMethodNames() {
		return supportedActions;
	}

}
